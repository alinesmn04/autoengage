"""
Main AutoEngage AI Agent.
"""

import os
import sys
import httpx
from pathlib import Path

# Force standard streams to use UTF-8 and safely replace unsupported characters
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="backslashreplace")
    except Exception:
        pass
if hasattr(sys.stderr, "reconfigure"):
    try:
        sys.stderr.reconfigure(encoding="utf-8", errors="backslashreplace")
    except Exception:
        pass

from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage
from dotenv import load_dotenv

# Load environment variables robustly
current_dir = Path(__file__).parent.resolve()
load_dotenv(current_dir / ".env")

from llm_helper import get_groq_api_key, rotate_groq_key

# Import all tools
from discovery_tools import *
from comment_tools import *
from content_tools import *
from lead_tools import *
from ads_tools import *
from dm_tools import *
from analytics_tools import *
from qa_tools import *
from voice_store import *
from platform_reddit import *
from platform_linkedin import *

# Create model based on configured provider
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

print(f"[LLM] AutoEngage using LLM Provider: {provider.upper()}")

if provider == "gemini":
    api_base = os.getenv("GEMINI_API_BASE")
    gemini_model = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
    client_kwargs = {}
    if api_base:
        client_kwargs["google_api_base"] = api_base
        
    llm = ChatGoogleGenerativeAI(
        model=gemini_model,
        temperature=0,
        max_output_tokens=1200,  # Token budget: cap responses
        request_timeout=120.0,
        max_retries=0,
        **client_kwargs
    )
elif provider == "groq":
    api_key = get_groq_api_key()
    api_base = os.getenv("GROQ_API_BASE", "https://api.groq.com/openai/v1")
    groq_model = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
    client_kwargs = {}
    if api_base:
        client_kwargs["openai_api_base"] = api_base
        
    groq_proxy = os.getenv("GROQ_PROXY")
    if groq_proxy:
        import httpx
        client_kwargs["http_client"] = httpx.Client(proxy=groq_proxy)
        client_kwargs["async_http_client"] = httpx.AsyncClient(proxy=groq_proxy)
        
    llm = ChatOpenAI(
        model=groq_model,
        openai_api_key=api_key,
        temperature=0,
        max_tokens=800,  # Token budget: cap Groq output
        max_retries=0,
        **client_kwargs
    )
elif provider == "openai":
    api_base = os.getenv("OPENAI_API_BASE")
    client_kwargs = {}
    if api_base:
        client_kwargs["openai_api_base"] = api_base
        
    llm = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0,
        max_retries=0,
        **client_kwargs
    )
else:
    raise ValueError(f"Unknown provider: {provider}")

# List of all tools
TOOLS = [
    search_viral_posts,
    read_post_content,
    score_relevance,

    draft_comment,
    qa_check_comment,

    generate_post_ideas,
    write_post,
    suggest_visual,
    ab_test_versions,

    create_lead_magnet_outline,
    generate_lead_magnet_pdf,
    write_cta_for_lead_magnet,
    capture_lead,

    research_competitor_ads,
    extract_ad_patterns,
    suggest_ad_copy,

    identify_warm_leads,
    draft_dm,
    track_conversation,

    analyze_engagement,
    generate_insights,
    score_lead,

    check_forbidden_phrases,
    check_ai_smell,
    fact_check,
    overall_quality_score,

    add_voice_sample,
    find_similar_voice,

    reddit_search_posts,
    reddit_read_post,
    reddit_post_comment,
    reddit_monitor_replies,

    linkedin_search_posts,
    linkedin_read_post,
    linkedin_post_comment
]

def get_groq_bound_llm(temperature=0):
    api_key = get_groq_api_key()
    api_base = os.getenv("GROQ_API_BASE", "https://api.groq.com/openai/v1")
    groq_model = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
    client_kwargs = {}
    if api_base:
        client_kwargs["openai_api_base"] = api_base
        
    groq_proxy = os.getenv("GROQ_PROXY")
    if groq_proxy:
        import httpx
        client_kwargs["http_client"] = httpx.Client(proxy=groq_proxy)
        client_kwargs["async_http_client"] = httpx.AsyncClient(proxy=groq_proxy)
        
    groq_llm = ChatOpenAI(
        model=groq_model,
        openai_api_key=api_key,
        temperature=temperature,
        max_tokens=800,  # Token budget: cap Groq output
        max_retries=0,
        **client_kwargs
    )
    return groq_llm.bind_tools(TOOLS)

# Bind tools to model
bound_llm = llm.bind_tools(TOOLS)

# Setup fallback LLM if main is gemini and GROQ_API_KEY is available
bound_fallback_llm = None
if provider == "gemini" and get_groq_api_key():
    bound_fallback_llm = get_groq_bound_llm()

def is_groq_model(model):
    if model is None:
        return False
    if hasattr(model, "bound"):
        return isinstance(model.bound, ChatOpenAI)
    return isinstance(model, ChatOpenAI)

class RetryingLLM:
    def __init__(self, bound_llm, bound_fallback_llm=None):
        self.bound_llm = bound_llm
        self.bound_fallback_llm = bound_fallback_llm

    def invoke(self, input, config=None, **kwargs):
        import time
        import re
        
        max_attempts = 5
        primary_failed = False
        last_err = None
        
        # 1. Try invoking primary LLM with rate limit retries
        for attempt in range(max_attempts):
            try:
                return self.bound_llm.invoke(input, config, **kwargs)
            except Exception as e:
                last_err = e
                err_str = str(e).lower()
                
                is_quota = "quota" in err_str or "exceeded" in err_str or "quota_exceeded" in err_str
                is_rate_limit = "429" in err_str or "resource_exhausted" in err_str or "rate limit" in err_str or "rate_limit" in err_str
                is_auth_error = "unauthenticated" in err_str or "401" in err_str or "invalid key" in err_str or "api_key" in err_str or "403" in err_str
                
                # If it's a credentials/auth error, we fallback immediately without retrying
                if is_auth_error:
                    print(f"\n[Auth Error] {e}. Skipping retries.")
                    primary_failed = True
                    break
                
                # If it's a quota limit or we exhausted retries
                if is_quota or (is_rate_limit and attempt == max_attempts - 1):
                    # Try rotating the Groq key if we are on Groq
                    if is_groq_model(self.bound_llm) and rotate_groq_key():
                        if attempt < max_attempts - 1:
                            print(f"[Groq Primary] Quota exceeded. Rotated to backup Groq key and retrying...")
                            self.bound_llm = get_groq_bound_llm()
                            continue
                    print(f"\n[Primary Quota/Limit] Skipping retries and falling back.")
                    primary_failed = True
                    break
                    
                if is_rate_limit:
                    if attempt < max_attempts - 1:
                        # Extract wait time
                        delay = 5.0
                        match = re.search(r"please (?:retry|try again) in ([\d.]+)s", err_str)
                        if match:
                            delay = float(match.group(1)) + 1.0 # add a small buffer
                        else:
                            match2 = re.search(r"['\"]retrydelay['\"]\s*:\s*['\"](\d+)s['\"]", err_str)
                            if match2:
                                delay = float(match2.group(1)) + 1.0
                            else:
                                delay = 5.0 * (attempt + 1) # backoff fallback
                        
                        if delay > 3.0:
                            # Try rotating the Groq key if we are on Groq
                            if is_groq_model(self.bound_llm) and rotate_groq_key():
                                if attempt < max_attempts - 1:
                                    print(f"[Groq Primary] Delay too high. Rotated to backup Groq key and retrying...")
                                    self.bound_llm = get_groq_bound_llm()
                                    continue
                            print(f"\n[Primary Rate Limit] Delay {delay:.2f}s is too high. Falling back immediately.")
                            primary_failed = True
                            break
                            
                        print(f"\n[Primary Rate Limit] Hit 429 quota/rate limit. Waiting {delay:.2f} seconds before retrying (attempt {attempt+1}/{max_attempts})...")
                        time.sleep(delay)
                        continue
                
                # For any other errors (like 500, network error, etc.), fallback immediately if fallback is available
                if self.bound_fallback_llm:
                    primary_failed = True
                    break
                raise e
        
        # 2. Try fallback LLM with rate limit retries
        if primary_failed and self.bound_fallback_llm:
            print(f"\nTrying fallback...")
            for fallback_attempt in range(max_attempts):
                try:
                    # If fallback is Groq, use the rotated key
                    if is_groq_model(self.bound_fallback_llm):
                        fallback_bound = get_groq_bound_llm()
                    else:
                        fallback_bound = self.bound_fallback_llm
                        
                    return fallback_bound.invoke(input, config, **kwargs)
                except Exception as fallback_err:
                    fb_err_str = str(fallback_err).lower()
                    is_fb_quota = "quota" in fb_err_str or "exceeded" in fb_err_str
                    is_fb_rate_limit = "429" in fb_err_str or "resource_exhausted" in fb_err_str or "rate_limit" in fb_err_str or "rate limit" in fb_err_str
                    
                    if is_fb_quota:
                        if is_groq_model(self.bound_fallback_llm) and rotate_groq_key():
                            if fallback_attempt < max_attempts - 1:
                                print(f"\n[Groq Fallback] Quota exceeded. Rotated to backup Groq key and retrying...")
                                continue
                        print(f"\n[Fallback Quota Error] Quota exceeded on fallback. Skipping retries.")
                        raise fallback_err
                        
                    if is_fb_rate_limit and fallback_attempt < max_attempts - 1:
                        # Extract wait time
                        delay = 5.0
                        match = re.search(r"please (?:retry|try again) in ([\d.]+)s", fb_err_str)
                        if match:
                            delay = float(match.group(1)) + 1.0
                        else:
                            delay = 5.0 * (fallback_attempt + 1)
                            
                        if delay > 3.0:
                            if is_groq_model(self.bound_fallback_llm) and rotate_groq_key():
                                print(f"\n[Groq Fallback] Delay too high. Rotated to backup Groq key and retrying...")
                                continue
                            print(f"\n[Fallback Rate Limit] Delay {delay:.2f}s is too high. Skipping retries.")
                            raise fallback_err
                            
                        print(f"\n[Fallback Rate Limit] Waiting {delay:.2f} seconds before retrying (attempt {fallback_attempt+1}/{max_attempts})...")
                        time.sleep(delay)
                        continue
                    print(f"\n[Fallback Error] Fallback failed: {fallback_err}")
                    raise fallback_err
        
        # If fallback is not available and primary failed, raise an exception
        if last_err:
            raise last_err
        raise RuntimeError("Primary LLM failed and no fallback LLM is configured.")

    def __getattr__(self, name):
        return getattr(self.bound_llm, name)

llm_with_tools = RetryingLLM(bound_llm, bound_fallback_llm)

# Create chat model specifically with Groq as primary (if available) and Gemini as fallback
chat_llm_with_tools = None

if get_groq_api_key():
    bound_chat_llm = get_groq_bound_llm(temperature=0)
    
    bound_chat_fallback_llm = None
    if os.getenv("GEMINI_API_KEY"):
        chat_gemini_base = os.getenv("GEMINI_API_BASE")
        chat_gemini_model = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
        chat_gemini_kwargs = {}
        if chat_gemini_base:
            chat_gemini_kwargs["google_api_base"] = chat_gemini_base
            
        chat_fallback_llm = ChatGoogleGenerativeAI(
            model=chat_gemini_model,
            temperature=0,
            max_output_tokens=1200,  # Token budget: cap responses
            request_timeout=120.0,
            max_retries=0,
            **chat_gemini_kwargs
        )
        bound_chat_fallback_llm = chat_fallback_llm.bind_tools(TOOLS)
        
    chat_llm_with_tools = RetryingLLM(bound_chat_llm, bound_chat_fallback_llm)
else:
    chat_llm_with_tools = llm_with_tools

SYSTEM_PROMPT = """You are AutoEngage, an autonomous marketing AI agent.
Tools: discover viral content, draft comments, QA checks, lead magnets, analytics, DMs.
Rules: reply in the user's language. Always add value. Never use forbidden phrases. QA before posting."""

if __name__ == "__main__":
    print("[Agent] AutoEngage Agent Started")
    
    tool_map = {tool.name: tool for tool in TOOLS}

    while True:
        user_input = input("\nYou: ")

        if user_input.lower() in ["exit", "quit"]:
            print("Goodbye!")
            break
            
        if not user_input.strip():
            continue

        messages = [
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=user_input)
        ]

        # Autonomous multi-turn loop
        max_iterations = 5  # Token budget: limit agent loops
        for iteration in range(max_iterations):
            try:
                response = chat_llm_with_tools.invoke(messages)
            except Exception as e:
                print(f"\n[Error] Error invoking LLM ({provider}): {e}")
                break
                
            messages.append(response)
            
            # Print agent thoughts if any
            if response.content:
                print(f"\nAgent: {response.content}")
                
            # Check for tool calls using standard LangChain unified tool_calls
            tool_calls = getattr(response, "tool_calls", [])
            
            # Fallback to additional_kwargs if tool_calls is empty
            if not tool_calls:
                add_kwargs_calls = response.additional_kwargs.get("tool_calls", [])
                if add_kwargs_calls:
                    import json
                    for tc in add_kwargs_calls:
                        func = tc.get("function", {})
                        try:
                            args = json.loads(func.get("arguments", "{}")) if isinstance(func.get("arguments"), str) else func.get("arguments")
                        except:
                            args = {}
                        tool_calls.append({
                            "id": tc.get("id"),
                            "name": func.get("name"),
                            "args": args
                        })
            
            if not tool_calls:
                break
                
            # Execute tools
            from langchain_core.messages import ToolMessage
            for tc in tool_calls:
                t_id = tc.get("id")
                t_name = tc.get("name")
                t_args = tc.get("args", {})
                
                print(f"[Tool Call] Executing '{t_name}' with args: {t_args}")
                
                if t_name in tool_map:
                    try:
                        t_res = tool_map[t_name].invoke(t_args)
                    except Exception as err:
                        t_res = f"Error during tool execution: {str(err)}"
                else:
                    t_res = f"Tool '{t_name}' not found."
                
                print(f"[Tool Result] {str(t_res)[:200]}...")
                
                messages.append(ToolMessage(content=str(t_res), tool_call_id=t_id))