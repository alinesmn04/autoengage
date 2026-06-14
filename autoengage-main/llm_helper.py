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

def _get_groq_llm(temperature=0.7):
    api_key = os.getenv("GROQ_API_KEY")
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
    if os.getenv("GROQ_API_KEY"):
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
        elif os.getenv("GROQ_API_KEY"):
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
    Generate clean text content from the LLM.
    """
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_prompt)
    ]
    
    # Try primary LLM
    try:
        llm = get_llm()
        res = llm.invoke(messages)
    except Exception as e:
        print(f"Error in primary LLM: {e}")
        
        # Check if primary provider was gemini, and if so try fallback
        primary_provider = os.getenv("LLM_PROVIDER")
        if not primary_provider:
            primary_provider = "gemini" if os.getenv("GEMINI_API_KEY") else "openai"
            
        if primary_provider == "gemini":
            fallback_llm = get_fallback_llm()
            if fallback_llm:
                print("Falling back to Groq...")
                try:
                    res = fallback_llm.invoke(messages)
                except Exception as fallback_err:
                    print(f"Fallback LLM (Groq) also failed: {fallback_err}")
                    return ""
            else:
                return ""
        else:
            return ""

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
