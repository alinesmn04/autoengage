import os
from pathlib import Path
from dotenv import load_dotenv
# import google.generativeai as genai
import httpx

# Load env
current_dir = Path(__file__).parent.resolve()
load_dotenv(current_dir / ".env")

print("--- Testing Gemini ---")
gemini_key = os.getenv("GEMINI_API_KEY")
print(f"Gemini Key starts with: {gemini_key[:10] if gemini_key else 'None'}...")
try:
    from langchain_google_genai import ChatGoogleGenerativeAI
    llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0)
    res = llm.invoke("Hello")
    print("Gemini Success:", res.content)
except Exception as e:
    print("Gemini Failed:", type(e), e)

print("\n--- Testing Groq ---")
groq_key = os.getenv("GROQ_API_KEY")
print(f"Groq Key starts with: {groq_key[:10] if groq_key else 'None'}...")
try:
    from langchain_openai import ChatOpenAI
    llm = ChatOpenAI(
        model="llama-3.1-8b-instant",
        openai_api_key=groq_key,
        openai_api_base="https://api.groq.com/openai/v1"
    )
    res = llm.invoke("Hello")
    print("Groq Success:", res.content)
except Exception as e:
    print("Groq Failed:", type(e), e)
