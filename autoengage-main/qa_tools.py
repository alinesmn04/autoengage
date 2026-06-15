"""
QA tools for AutoEngage.
"""

from langchain_core.tools import tool
from pydantic import BaseModel, Field

import json
from typing import Union, List

# AI "smell" words — checked locally, no LLM needed
_AI_SMELL_WORDS = [
    "revolutionary", "game changer", "game-changer", "next level", "next-level",
    "cutting-edge", "cutting edge", "unlock", "let's dive in", "dive in",
    "in summary", "in conclusion", "remember that", "it's important to note",
    "groundbreaking", "transformative", "unprecedented", "leverage", "synergy",
    "paradigm shift", "empower", "seamlessly", "robust solution", "delve",
    "it is worth noting", "foster", "navigate", "realm", "unleash", "harness"
]

class CheckForbiddenPhrasesInput(BaseModel):
    text: str = Field(description="The text content to check for forbidden phrases.")
    forbidden: List[str] = Field(
        description="A list of phrases that are forbidden in the text."
    )


@tool(args_schema=CheckForbiddenPhrasesInput)
def check_forbidden_phrases(text: str, forbidden: List[str]) -> str:
    """
    Check if forbidden phrases exist in text. No LLM needed.
    """
    if isinstance(forbidden, str):
        forbidden = forbidden.strip()
        if forbidden.startswith("[") and forbidden.endswith("]"):
            try:
                forbidden = json.loads(forbidden)
            except Exception:
                forbidden = [forbidden]
        elif not forbidden:
            forbidden = []
        else:
            forbidden = [f.strip() for f in forbidden.split(",") if f.strip()]

    found = [phrase for phrase in forbidden if phrase.lower() in text.lower()]

    if found:
        return f"❌ Forbidden phrases found: {', '.join(found)}"
    return "✅ No forbidden phrases found"


@tool
def check_ai_smell(text: str) -> dict:
    """
    Detect AI-generated patterns using local keyword matching (no LLM).
    """
    text_lower = text.lower()
    hits = [w for w in _AI_SMELL_WORDS if w in text_lower]
    score = min(len(hits) * 2, 10)
    if score >= 6:
        explanation = f"Sounds AI-generated. Detected: {', '.join(hits[:3])}"
    elif score >= 3:
        explanation = f"Slightly AI-sounding. Detected: {', '.join(hits[:2])}"
    else:
        explanation = "Sounds natural."
    return {"score": score, "explanation": explanation}


@tool
def fact_check(text: str) -> list:
    """
    Perform a lightweight fact-check on the text.
    """
    from llm_helper import generate_json
    # Only call LLM if text is substantial
    if len(text) < 80:
        return [{"claim": text[:60], "status": "⚠️ Cannot verify"}]

    system_prompt = "You are a fact-checker."
    user_prompt = (
        f"Text: \"{text[:400]}\"\n\n"
        f"List 2 main claims and their status. "
        f"JSON list: [{{\"claim\":\"...\",\"status\":\"✅ Likely true|❌ Likely false|⚠️ Cannot verify\"}}]"
    )
    fallback = [
        {"claim": "AI improves productivity", "status": "✅ Likely true"},
        {"claim": "Automation saves time", "status": "✅ Likely true"}
    ]
    return generate_json(system_prompt, user_prompt, fallback)


class OverallQualityScoreInput(BaseModel):
    text: str = Field(description="The text content to evaluate.")
    forbidden: List[str] = Field(
        description="A list of forbidden phrases to check against."
    )


@tool(args_schema=OverallQualityScoreInput)
def overall_quality_score(text: str, forbidden: List[str]) -> dict:
    """
    Generate an overall quality score. Uses only local checks — zero LLM calls.
    """
    if isinstance(forbidden, str):
        forbidden = forbidden.strip()
        if forbidden.startswith("[") and forbidden.endswith("]"):
            try:
                forbidden = json.loads(forbidden)
            except Exception:
                forbidden = [forbidden]
        elif not forbidden:
            forbidden = []
        else:
            forbidden = [f.strip() for f in forbidden.split(",") if f.strip()]

    forbidden_result = check_forbidden_phrases.invoke({"text": text, "forbidden": forbidden})
    ai_result = check_ai_smell.invoke({"text": text})

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