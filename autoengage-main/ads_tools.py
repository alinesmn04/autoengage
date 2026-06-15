"""
Advertising research tools for AutoEngage.
"""

from langchain_core.tools import tool
from llm_helper import generate_text, generate_json


@tool
def research_competitor_ads(competitor_name: str) -> str:
    """
    Analyze competitor advertising style.
    """
    system_prompt = "Competitive marketing researcher."
    user_prompt = (
        f"Brief analysis of \"{competitor_name[:80]}\" ad strategy:\n"
        f"- Main messaging angle\n- CTA style\n- Core value prop\n- Target pain point\n"
        f"Keep it concise, max 150 words."
    )
    return generate_text(system_prompt, user_prompt)


@tool
def extract_ad_patterns(data_ads: str) -> list:
    """
    Extract common advertising patterns.
    """
    system_prompt = "Ad strategist extracting copywriting patterns."
    user_prompt = (
        f"From these ads: {data_ads[:400]}\n"
        f"Extract 3 key patterns. JSON list of strings."
    )
    fallback = [
        "Use emotional hooks",
        "Short CTA sentences",
        "Focus on customer problems"
    ]
    return generate_json(system_prompt, user_prompt, fallback)


@tool
def suggest_ad_copy(patterns: str, brand_tone: str) -> list:
    """
    Generate ad copy ideas based on ad patterns.
    """
    system_prompt = f"Conversion copywriter. Tone: {brand_tone}."
    user_prompt = (
        f"Patterns: {patterns[:300]}\n"
        f"Write 3 short ad copies. JSON list of strings."
    )
    fallback = [
        "Save hours every week with smart AI automation.",
        "Your business deserves simpler workflows.",
        "Automate repetitive tasks and focus on growth."
    ]
    return generate_json(system_prompt, user_prompt, fallback)