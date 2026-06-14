import os
import json
from pathlib import Path
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

# Load env variables robustly
current_dir = Path(__file__).parent.resolve()
load_dotenv(current_dir / ".env")

# Groq API Key Rotation
GROQ_KEYS = [k for k in [os.getenv("GROQ_API_KEY"), os.getenv("GROQ_API_KEY_BACKUP")] if k]
current_groq_key_index = 0

def get_groq_api_key():
    if not GROQ_KEYS:
        return None
    return GROQ_KEYS[current_groq_key_index]

def rotate_groq_key():
    global current_groq_key_index
    if len(GROQ_KEYS) > 1:
        current_groq_key_index = (current_groq_key_index + 1) % len(GROQ_KEYS)
        print(f"\n[Groq Rotation] Rotated to key index {current_groq_key_index} (Key starts with: {get_groq_api_key()[:10]}...)")
        return True
    return False

def _get_groq_llm(temperature=0.7):
    api_key = get_groq_api_key()
    api_base = os.getenv("GROQ_API_BASE", "https://api.groq.com/openai/v1")
    model = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
    kwargs = {}
    if api_base:
        kwargs["openai_api_base"] = api_base
    groq_proxy = os.getenv("GROQ_PROXY")
    if groq_proxy:
        import httpx
        kwargs["http_client"] = httpx.Client(proxy=groq_proxy)
        kwargs["async_http_client"] = httpx.AsyncClient(proxy=groq_proxy)
    return ChatOpenAI(model=model, openai_api_key=api_key, temperature=temperature, max_retries=0, **kwargs)

def get_fallback_llm(temperature=0.7):
    if get_groq_api_key():
        try:
            return _get_groq_llm(temperature=temperature)
        except Exception as e:
            print(f"Error creating fallback Groq LLM: {e}")
    return None

def get_llm():
    provider = os.getenv("LLM_PROVIDER")
    if not provider:
        if os.getenv("GEMINI_API_KEY"):
            provider = "gemini"
        elif get_groq_api_key():
            provider = "groq"
        elif os.getenv("OPENAI_API_KEY"):
            provider = "openai"
        else:
            provider = "gemini"
            
    if provider == "gemini":
        model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
        api_base = os.getenv("GEMINI_API_BASE")
        kwargs = {}
        if api_base:
            kwargs["google_api_base"] = api_base
        return ChatGoogleGenerativeAI(model=model, temperature=0.7, max_retries=0, **kwargs)
    elif provider == "openai":
        api_base = os.getenv("OPENAI_API_BASE")
        kwargs = {}
        if api_base:
            kwargs["openai_api_base"] = api_base
        return ChatOpenAI(model="gpt-4o-mini", temperature=0.7, max_retries=0, **kwargs)
    elif provider == "groq":
        return _get_groq_llm()
    else:
        raise ValueError(f"Unknown or unsupported provider: {provider}")

def generate_text(system_prompt: str, user_prompt: str) -> str:
    """
    Generate clean text content from the LLM with robust retries and fallback.
    """
    import time
    import re
    
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_prompt)
    ]
    
    primary_provider = os.getenv("LLM_PROVIDER")
    if not primary_provider:
        primary_provider = "gemini" if os.getenv("GEMINI_API_KEY") else "openai"
        
    max_attempts = 5
    res = None
    
    # 1. Try invoking primary LLM with rate limit retries
    for attempt in range(max_attempts):
        try:
            llm = get_llm()
            res = llm.invoke(messages)
            break
        except Exception as e:
            err_str = str(e).lower()
            is_quota = "quota" in err_str or "exceeded" in err_str
            is_rate_limit = "429" in err_str or "resource_exhausted" in err_str or "rate limit" in err_str or "rate_limit" in err_str
            is_auth_error = "unauthenticated" in err_str or "401" in err_str or "invalid key" in err_str or "api_key" in err_str or "403" in err_str
            
            # For auth or quota errors, we skip retry and try fallback immediately
            if is_auth_error or is_quota:
                print(f"Authentication or Quota error in primary LLM: {e}. Skipping retries.")
                break
                
            if is_rate_limit and attempt < max_attempts - 1:
                delay = 5.0
                match = re.search(r"please (?:retry|try again) in ([\d.]+)s", err_str)
                if match:
                    delay = float(match.group(1)) + 1.0
                else:
                    delay = 5.0 * (attempt + 1)
                
                # If delay is too high, don't block the request - try fallback immediately
                if delay > 3.0:
                    print(f"[Primary LLM Rate Limit] Delay {delay:.2f}s is too high. Skipping retries.")
                    break
                    
                print(f"[Primary LLM Rate Limit] Waiting {delay:.2f} seconds before retrying (attempt {attempt+1}/{max_attempts})...")
                time.sleep(delay)
                continue
            
            print(f"Error in primary LLM: {e}")
            break

    # 2. If primary failed, try fallback (Groq) with rate limit retries
    if res is None and primary_provider == "gemini":
        fallback_llm = get_fallback_llm()
        if fallback_llm:
            print("Trying Groq fallback LLM...")
            for fallback_attempt in range(max_attempts):
                try:
                    res = fallback_llm.invoke(messages)
                    break
                except Exception as fallback_err:
                    fb_err_str = str(fallback_err).lower()
                    is_fb_quota = "quota" in fb_err_str or "exceeded" in fb_err_str
                    is_fb_rate_limit = "429" in fb_err_str or "resource_exhausted" in fb_err_str or "rate_limit" in fb_err_str or "rate limit" in fb_err_str
                    
                    if is_fb_quota:
                        # Try rotating the Groq key!
                        if rotate_groq_key():
                            print(f"[Groq Fallback] Quota exceeded. Rotated to backup Groq key and retrying...")
                            fallback_llm = get_fallback_llm()
                            continue
                        print(f"Quota error in fallback LLM: {fallback_err}. Skipping retries.")
                        break
                        
                    if is_fb_rate_limit and fallback_attempt < max_attempts - 1:
                        delay = 5.0
                        match = re.search(r"please (?:retry|try again) in ([\d.]+)s", fb_err_str)
                        if match:
                            delay = float(match.group(1)) + 1.0
                        else:
                            delay = 5.0 * (fallback_attempt + 1)
                            
                        if delay > 3.0:
                            print(f"[Fallback Rate Limit] Delay {delay:.2f}s is too high. Skipping retries.")
                            break
                            
                        print(f"[Groq Fallback Rate Limit] Waiting {delay:.2f} seconds before retrying (attempt {fallback_attempt+1}/{max_attempts})...")
                        time.sleep(delay)
                        continue
                    
                    print(f"Fallback LLM (Groq) also failed: {fallback_err}")
                    break

    try:
        content = res.content
        if isinstance(content, list):
            text_parts = []
            for item in content:
                if isinstance(item, dict) and "text" in item:
                    text_parts.append(item["text"])
                elif isinstance(item, str):
                    text_parts.append(item)
            content = "".join(text_parts)
        elif content is None:
            content = ""
        else:
            content = str(content)
            
        return content.strip()
    except Exception as e:
        print(f"Error parsing LLM response: {e}")
        return ""

def generate_json(system_prompt: str, user_prompt: str, fallback_dict: dict) -> dict:
    """
    Generate and parse a JSON object from the LLM.
    """
    prompt = user_prompt + "\n\nIMPORTANT: Return ONLY a valid JSON object matching the requested structure. Do not include any markdown formatting or surrounding text, just the raw JSON."
    res_text = generate_text(system_prompt, prompt)
    if not res_text:
        return fallback_dict
    
    # Strip markdown block formatting if present
    clean_text = res_text.strip()
    if clean_text.startswith("```json"):
        clean_text = clean_text[7:]
    elif clean_text.startswith("```"):
        clean_text = clean_text[3:]
    if clean_text.endswith("```"):
        clean_text = clean_text[:-3]
    clean_text = clean_text.strip()
    
    try:
        return json.loads(clean_text)
    except Exception as e:
        print(f"Error parsing JSON: {e}. Raw text was: {res_text}")
        return fallback_dict
