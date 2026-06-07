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
    system_prompt = "You are a competitive intelligence marketing researcher."
    user_prompt = (
        f"Analyze the advertising and marketing messaging style of the competitor \"{competitor_name}\".\n\n"
        f"Return a structured breakdown detailing:\n"
        f"- What they focus on (messaging angles)\n"
        f"- Their typical CTA styles\n"
        f"- Their core value propositions\n"
        f"- The customer pain points they target."
    )
    return generate_text(system_prompt, user_prompt)


@tool
def extract_ad_patterns(data_ads: str) -> list:
    """
    Extract common advertising patterns.
    """
    system_prompt = "You are an advertising strategist specializing in extracting copywriting pattern formulas."
    user_prompt = (
        f"Analyze these competitor ads / marketing descriptions:\n{data_ads}\n\n"
        f"Extract exactly 5 recurring, high-converting copywriting patterns, formulas, or strategies used here. "
        f"Return them as a JSON list of strings."
    )
    fallback = [
        "Use emotional hooks",
        "Short CTA sentences",
        "Focus on customer problems",
        "Highlight time-saving benefits",
        "Use simple language"
    ]
    return generate_json(system_prompt, user_prompt, fallback)


@tool
def suggest_ad_copy(patterns: str, brand_tone: str) -> list:
    """
    Generate ad copy ideas based on ad patterns.
    """
    system_prompt = f"You are a conversion copywriter writing high-converting ad copy using the tone: {brand_tone}."
    user_prompt = (
        f"Using these copywriting patterns/formulas: {patterns}\n\n"
        f"Draft exactly 3 high-converting, distinct ad copy variations. Return them as a JSON list of strings."
    )
    fallback = [
        "Save hours every week with smart AI automation.",
        "Your business deserves simpler workflows and faster results.",
        "Automate repetitive tasks and focus on growth."
    ]
    return generate_json(system_prompt, user_prompt, fallback)