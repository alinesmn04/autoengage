"""
QA tools for AutoEngage.
"""

from langchain_core.tools import tool


@tool
def check_forbidden_phrases(text: str, forbidden: list) -> str:
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

    ai_words = [
        "revolutionary",
        "game changer",
        "unlock",
        "next level",
        "cutting-edge"
    ]

    matches = 0

    for word in ai_words:
        if word.lower() in text.lower():
            matches += 1

    score = min(matches * 2, 10)

    if score <= 3:
        explanation = "Text sounds natural"
    elif score <= 6:
        explanation = "Text slightly sounds AI-generated"
    else:
        explanation = "Text strongly sounds AI-generated"

    return {
        "score": score,
        "explanation": explanation
    }


@tool
def fact_check(text: str) -> list:
    """
    Simple fact-check simulation.
    """

    return [
        {"claim": "AI improves productivity", "status": "✅ Likely true"},
        {"claim": "Automation saves time", "status": "✅ Likely true"},
        {"claim": "Guaranteed business growth", "status": "⚠️ Cannot verify"}
    ]


@tool
def overall_quality_score(text: str, forbidden: list) -> dict:
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

    score -= ai_result["score"] * 3

    if len(text) < 50:
        score -= 20

    score = max(score, 0)

    return {
        "overall_score": score,
        "forbidden_check": forbidden_result,
        "ai_smell": ai_result,
        "length": len(text)
    }