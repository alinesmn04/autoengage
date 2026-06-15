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

# ──────────────────────────────────────────────
# Groq API Key Rotation
# ──────────────────────────────────────────────
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
    if not api_key:
        return None
    api_base = os.getenv("GROQ_API_BASE", "https://api.groq.com/openai/v1")
    model = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")
    kwargs = {"openai_api_base": api_base}
    groq_proxy = os.getenv("GROQ_PROXY")
    if groq_proxy:
        import httpx
        kwargs["http_client"] = httpx.Client(proxy=groq_proxy)
        kwargs["async_http_client"] = httpx.AsyncClient(proxy=groq_proxy)
    return ChatOpenAI(
        model=model,
        openai_api_key=api_key,
        temperature=temperature,
        max_tokens=800,  # Token budget: cap Groq output
        max_retries=0,
        **kwargs
    )

def get_fallback_llm(temperature=0.7):
    """Return a Groq LLM as fallback, or None if unavailable."""
    if get_groq_api_key():
        try:
            return _get_groq_llm(temperature=temperature)
        except Exception as e:
            print(f"[Fallback] Error creating Groq LLM: {e}")
    return None

def get_llm():
    """Return the primary LLM based on LLM_PROVIDER env var."""
    provider = os.getenv("LLM_PROVIDER", "").lower()

    # Auto-detect provider if not set
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
        # Default to gemini-2.0-flash — fast, cheap, and available
        model = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
        kwargs = {}
        api_base = os.getenv("GEMINI_API_BASE")
        if api_base:
            kwargs["google_api_base"] = api_base
        return ChatGoogleGenerativeAI(
            model=model,
            temperature=0.7,
            max_output_tokens=1200,  # Token budget: cap output
            max_retries=0,
            **kwargs
        )
    elif provider == "openai":
        api_base = os.getenv("OPENAI_API_BASE")
        kwargs = {}
        if api_base:
            kwargs["openai_api_base"] = api_base
        return ChatOpenAI(
            model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            temperature=0.7,
            max_retries=0,
            **kwargs
        )
    elif provider == "groq":
        llm = _get_groq_llm()
        if llm:
            return llm
        raise RuntimeError("GROQ provider selected but no valid GROQ_API_KEY found.")
    else:
        raise ValueError(f"Unknown or unsupported LLM provider: '{provider}'. Use 'gemini', 'openai', or 'groq'.")


# ──────────────────────────────────────────────
# Error classification helpers
# ──────────────────────────────────────────────

def _is_auth_error(err_str: str) -> bool:
    return any(k in err_str for k in [
        "unauthenticated", "401", "invalid key", "api_key",
        "403", "permission denied", "invalid api key"
    ])

def _is_quota_error(err_str: str) -> bool:
    if "rate_limit" in err_str or "rate limit" in err_str or "429" in err_str or "resource_exhausted" in err_str:
        return False
    return any(k in err_str for k in ["quota", "exceeded", "billing"])

def _is_rate_limit_error(err_str: str) -> bool:
    return any(k in err_str for k in [
        "429", "resource_exhausted", "rate limit", "rate_limit",
        "too many requests"
    ])

def _is_token_error(err_str: str) -> bool:
    """Detect context window / token limit errors."""
    return any(k in err_str for k in [
        "context window", "token", "maximum context length",
        "too long", "content too large", "string too long"
    ])

def _extract_retry_delay(err_str: str, attempt: int, default_step: float = 5.0) -> float:
    """Parse suggested retry delay from error message, or use exponential backoff."""
    import re
    match = re.search(r"please (?:retry|try again) in ([\d.]+)s", err_str)
    if match:
        return float(match.group(1)) + 1.0
    return default_step * (attempt + 1)


# ──────────────────────────────────────────────
# Core generation function
# ──────────────────────────────────────────────

def generate_text(system_prompt: str, user_prompt: str) -> str:
    """
    Generate clean text content from the LLM with robust retries and Groq fallback.
    Strategy:
      1. Try primary LLM up to max_attempts times (with smart retry/skip logic).
      2. On failure, fall back to Groq (with key rotation on quota errors).
      3. Return empty string only as last resort.
    """
    import time

    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_prompt)
    ]

    max_attempts = 4
    res = None

    # ── Step 1: Try primary LLM ──────────────────────────────────────────────
    for attempt in range(max_attempts):
        try:
            llm = get_llm()
            res = llm.invoke(messages)
            break  # Success
        except Exception as e:
            err_str = str(e).lower()

            if _is_auth_error(err_str):
                print(f"[Primary LLM] Auth error (bad API key?): {e}")
                break  # No point retrying with same key

            if _is_quota_error(err_str):
                print(f"[Primary LLM] Quota exceeded: {e}")
                break  # Skip retries — go straight to fallback

            if _is_token_error(err_str):
                print(f"[Primary LLM] Token/context limit error: {e}")
                # Truncate user prompt and retry once
                if attempt == 0:
                    user_prompt = user_prompt[:3000]
                    messages = [
                        SystemMessage(content=system_prompt),
                        HumanMessage(content=user_prompt)
                    ]
                    print("[Primary LLM] Truncated prompt to 3000 chars, retrying...")
                    continue
                break

            if _is_rate_limit_error(err_str) and attempt < max_attempts - 1:
                delay = _extract_retry_delay(err_str, attempt)
                if delay > 8.0:
                    print(f"[Primary LLM Rate Limit] Retry delay {delay:.1f}s is too high — switching to fallback.")
                    break
                print(f"[Primary LLM Rate Limit] Waiting {delay:.1f}s before retry {attempt + 1}/{max_attempts}...")
                time.sleep(delay)
                continue

            print(f"[Primary LLM] Unexpected error (attempt {attempt + 1}): {e}")
            break

    # ── Step 2: Groq fallback ────────────────────────────────────────────────
    if res is None:
        fallback_llm = get_fallback_llm()
        if fallback_llm:
            print("[Fallback] Switching to Groq LLM...")
            for fb_attempt in range(max_attempts):
                try:
                    res = fallback_llm.invoke(messages)
                    print("[Fallback] Groq responded successfully.")
                    break
                except Exception as fallback_err:
                    fb_err_str = str(fallback_err).lower()

                    if _is_auth_error(fb_err_str):
                        if rotate_groq_key():
                            print("[Groq Fallback] Auth error (bad key) — rotated to backup key, retrying...")
                            fallback_llm = get_fallback_llm()
                            continue
                        print(f"[Groq Fallback] All keys invalid or auth failed: {fallback_err}")
                        break

                    if _is_quota_error(fb_err_str):
                        if rotate_groq_key():
                            print("[Groq Fallback] Quota exceeded — rotated to backup key, retrying...")
                            fallback_llm = get_fallback_llm()
                            continue
                        print(f"[Groq Fallback] All keys quota exceeded: {fallback_err}")
                        break

                    if _is_rate_limit_error(fb_err_str) and fb_attempt < max_attempts - 1:
                        delay = _extract_retry_delay(fb_err_str, fb_attempt)
                        if delay > 8.0:
                            if rotate_groq_key():
                                print(f"[Groq Fallback] Retry delay {delay:.1f}s too high — rotated key, retrying...")
                                fallback_llm = get_fallback_llm()
                                continue
                            if delay <= 15.0:
                                print(f"[Groq Fallback Rate Limit] Delay {delay:.1f}s is high but no backup key. Waiting and retrying...")
                                time.sleep(delay)
                                continue
                            print(f"[Groq Fallback] Retry delay {delay:.1f}s too high — aborting.")
                            break
                        print(f"[Groq Fallback Rate Limit] Waiting {delay:.1f}s (attempt {fb_attempt + 1}/{max_attempts})...")
                        time.sleep(delay)
                        continue

                    print(f"[Groq Fallback] Error (attempt {fb_attempt + 1}): {fallback_err}")
                    break
        else:
            print("[Fallback] No Groq API key configured — cannot fall back.")

    # ── Step 3: Parse response ───────────────────────────────────────────────
    if res is None:
        print("[LLM] All providers failed. Returning empty string.")
        return ""

    try:
        content = res.content
        if isinstance(content, list):
            parts = []
            for item in content:
                if isinstance(item, dict) and "text" in item:
                    parts.append(item["text"])
                elif isinstance(item, str):
                    parts.append(item)
            content = "".join(parts)
        elif content is None:
            content = ""
        else:
            content = str(content)
        return content.strip()
    except Exception as e:
        print(f"[LLM] Error parsing response: {e}")
        return ""


def generate_json(system_prompt: str, user_prompt: str, fallback_dict: dict) -> dict:
    """
    Generate and parse a JSON object from the LLM.
    Returns fallback_dict on any parse failure.
    """
    prompt = (
        user_prompt
        + "\n\nIMPORTANT: Return ONLY a valid JSON object matching the requested structure. "
        "Do not include any markdown formatting or surrounding text, just the raw JSON."
    )
    res_text = generate_text(system_prompt, prompt)
    if not res_text:
        return fallback_dict

    # Strip markdown code fences if present
    clean_text = res_text.strip()
    for prefix in ("```json", "```"):
        if clean_text.startswith(prefix):
            clean_text = clean_text[len(prefix):]
            break
    if clean_text.endswith("```"):
        clean_text = clean_text[:-3]
    clean_text = clean_text.strip()

    try:
        return json.loads(clean_text)
    except Exception as e:
        print(f"[LLM] JSON parse error: {e}. Raw text: {res_text[:200]}")
        return fallback_dict
