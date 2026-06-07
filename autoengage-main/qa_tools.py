"""
QA tools for AutoEngage.
"""

from langchain_core.tools import tool
from pydantic import BaseModel, Field


class CheckForbiddenPhrasesInput(BaseModel):
    text: str = Field(description="The text content to check for forbidden phrases.")
    forbidden: list[str] = Field(description="A list of phrases that are forbidden in the text.")


@tool(args_schema=CheckForbiddenPhrasesInput)
def check_forbidden_phrases(text: str, forbidden: list[str]) -> str:
    """
    Check if forbidden phrases exist in text.
    """

    found = []

    for phrase in forbidden:
        if phrase.lower() in text.lower():
            found.append(phrase)

    if found:
        return f"❌ Forbidden phrases found: {', '.join(found)}"

    return "✅ No forbidden phrases found"


@tool
def check_ai_smell(text: str) -> dict:
    """
    Estimate how AI-generated a text sounds.
    """
    from llm_helper import generate_json
    system_prompt = "You are an expert editor who can spot generic, overly-enthusiastic AI-generated text."
    user_prompt = (
        f"Analyze this text:\n\"{text}\"\n\n"
        f"Rate how much it sounds like a generic ChatGPT/AI output (score from 0 to 10, where 10 is extremely AI-smelling "
        f"using words like revolutionary, game changer, next level, cutting-edge, unlock, let's dive in, remember that, in summary, etc., "
        f"and 0 is completely natural human copywriting).\n\n"
        f"Return a JSON object with exactly these keys:\n"
        f"- \"score\": The integer score from 0 to 10.\n"
        f"- \"explanation\": A short explanation of your score."
    )
    fallback = {
        "score": 2,
        "explanation": "Text sounds natural"
    }
    return generate_json(system_prompt, user_prompt, fallback)


@tool
def fact_check(text: str) -> list:
    """
    Perform a dynamic fact-check.
    """
    from llm_helper import generate_json
    system_prompt = "You are a professional fact-checker."
    user_prompt = (
        f"Analyze the claims in the following text:\n\"{text}\"\n\n"
        f"Extract the top 3 claims made and verify if they are likely true, false, or unverifiable.\n"
        f"Return a JSON list of dictionaries. Each dictionary must have:\n"
        f"- \"claim\": The claim text\n"
        f"- \"status\": One of: \"✅ Likely true\", \"❌ Likely false\", or \"⚠️ Cannot verify\" with a brief reason."
    )
    fallback = [
        {"claim": "AI improves productivity", "status": "✅ Likely true"},
        {"claim": "Automation saves time", "status": "✅ Likely true"},
        {"claim": "Guaranteed business growth", "status": "⚠️ Cannot verify"}
    ]
    return generate_json(system_prompt, user_prompt, fallback)


class OverallQualityScoreInput(BaseModel):
    text: str = Field(description="The text content to evaluate.")
    forbidden: list[str] = Field(description="A list of forbidden phrases to check against.")


@tool(args_schema=OverallQualityScoreInput)
def overall_quality_score(text: str, forbidden: list[str]) -> dict:
    """
    Generate an overall quality score.
    """

    forbidden_result = check_forbidden_phrases.invoke({
        "text": text,
        "forbidden": forbidden
    })

    ai_result = check_ai_smell.invoke({
        "text": text
    })

    score = 100

    if "❌" in forbidden_result:
        score -= 30

    score -= ai_result.get("score", 2) * 3

    if len(text) < 50:
        score -= 20

    score = max(score, 0)

    return {
        "overall_score": score,
        "forbidden_check": forbidden_result,
        "ai_smell": ai_result,
        "length": len(text)
    }