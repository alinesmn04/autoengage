"""
Comment tools for AutoEngage.

This module creates comments and performs QA checks
before publishing.
"""

from langchain_core.tools import tool


@tool
def draft_comment(post_summary: str, brand_tone: str, cta: str) -> str:
    """
    Generate a marketing comment based on a post summary.
    """

    comment = (
        f"Great insights! I really liked your point about {post_summary[:40]}.\n\n"
        f"Many businesses still struggle with this, and smart automation can really help.\n\n"
        f"{cta}"
    )

    return comment


@tool
def qa_check_comment(comment: str, phrases_forbidden: list) -> dict:
    """
    Perform QA checks on a generated comment.
    """

    result = {}

    # Forbidden phrases check
    forbidden_found = []

    for phrase in phrases_forbidden:
        if phrase.lower() in comment.lower():
            forbidden_found.append(phrase)

    if forbidden_found:
        result["forbidden_check"] = f"❌ Found forbidden phrases: {', '.join(forbidden_found)}"
    else:
        result["forbidden_check"] = "✅ No forbidden phrases"

    # AI smell check
    ai_words = ["revolutionary", "unlock", "game changer", "next level"]

    ai_found = any(word in comment.lower() for word in ai_words)

    if ai_found:
        result["ai_smell"] = "⚠️ Comment sounds AI-generated"
    else:
        result["ai_smell"] = "✅ Comment sounds natural"

    # Value check
    if len(comment.split()) > 12:
        result["value_check"] = "✅ Comment contains meaningful value"
    else:
        result["value_check"] = "❌ Comment is too short"

    # Length check
    if 50 <= len(comment) <= 500:
        result["length_check"] = "✅ Comment length is valid"
    else:
        result["length_check"] = "❌ Comment length is invalid"

    return result 