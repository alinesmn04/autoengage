"""
Comment tools for AutoEngage.
"""

from langchain_core.tools import tool
from pydantic import BaseModel, Field
from llm_helper import generate_text, generate_json
import json
from typing import List


@tool
def draft_comment(post_summary: str, brand_tone: str, cta: str) -> str:
    """
    Generate a marketing comment based on a post summary.
    """
    system_prompt = f"Marketing agent. Tone: {brand_tone}. Write engaging social media comments."
    user_prompt = (
        f"Post: \"{post_summary[:250]}\"\n"
        f"Write a short valuable comment (2-3 sentences) that adds to the discussion. "
        f"End naturally with: {cta}"
    )
    res = generate_text(system_prompt, user_prompt)
    if not res:
        res = f"Great insights! Automation can really help scale business efficiency. {cta}"
    return res


class QaCheckCommentInput(BaseModel):
    comment: str = Field(description="The comment text to perform QA checks on.")
    phrases_forbidden: List[str] = Field(
        description="List of forbidden phrases that must not appear in the comment."
    )


@tool(args_schema=QaCheckCommentInput)
def qa_check_comment(comment: str, phrases_forbidden: List[str]) -> dict:
    """
    Perform QA checks on a generated comment. Uses local checks — no LLM.
    """
    if isinstance(phrases_forbidden, str):
        phrases_forbidden = phrases_forbidden.strip()
        if phrases_forbidden.startswith("[") and phrases_forbidden.endswith("]"):
            try:
                phrases_forbidden = json.loads(phrases_forbidden)
            except Exception:
                phrases_forbidden = [phrases_forbidden]
        elif not phrases_forbidden:
            phrases_forbidden = []
        else:
            phrases_forbidden = [p.strip() for p in phrases_forbidden.split(",") if p.strip()]

    found = [p for p in phrases_forbidden if p.lower() in comment.lower()]
    forbidden_check = f"❌ Found: {', '.join(found)}" if found else "✅ No forbidden phrases"

    # Local AI-smell check
    ai_words = ["revolutionary", "game changer", "cutting-edge", "unlock", "leverage",
                 "seamlessly", "groundbreaking", "transformative", "delve", "unleash"]
    ai_hits = [w for w in ai_words if w in comment.lower()]
    ai_smell = f"⚠️ Sounds AI-generated ({', '.join(ai_hits[:2])})" if ai_hits else "✅ Comment sounds natural"

    value_check = "✅ Comment contains meaningful value" if len(comment) > 40 else "❌ Comment is too short"
    length_check = "✅ Comment length is valid" if 20 <= len(comment) <= 1000 else "❌ Comment length is invalid"

    return {
        "forbidden_check": forbidden_check,
        "ai_smell": ai_smell,
        "value_check": value_check,
        "length_check": length_check
    }