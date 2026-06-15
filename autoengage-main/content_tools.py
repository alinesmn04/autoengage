"""
Content creation tools for AutoEngage.
"""

from langchain_core.tools import tool
from llm_helper import generate_text, generate_json


@tool
def generate_post_ideas(niche: str, count: int = 3) -> list:
    """
    Generate post ideas for a niche.
    """
    system_prompt = "Social media content strategist."
    user_prompt = (
        f"Give {count} high-engagement post ideas for: {niche[:100]}. "
        f"JSON list of strings only."
    )
    fallback = [f"How {niche} can improve productivity"] * count
    return generate_json(system_prompt, user_prompt, fallback)


@tool
def write_post(idea: str, platform: str, tone: str) -> str:
    """
    Generate a social media post adapted to a platform.
    """
    system_prompt = f"Copywriter. Platform: {platform}. Tone: {tone}."
    user_prompt = (
        f"Write a post about: \"{idea[:200]}\"\n"
        f"Platform rules: LinkedIn=professional+hashtags, Reddit=conversational, Twitter=<280 chars."
    )
    res = generate_text(system_prompt, user_prompt)
    if not res:
        res = f"Here is our take on: {idea}. Success starts with clear goals. #{platform} #success"
    return res


@tool
def suggest_visual(post_text: str) -> list:
    """
    Suggest visual ideas for a post.
    """
    system_prompt = "Art director suggesting social media visuals."
    user_prompt = (
        f"Post: \"{post_text[:150]}\"\n"
        f"Suggest 3 visual ideas. JSON list of strings."
    )
    fallback = [
        "AI dashboard screenshot",
        "Business owner using automation",
        "Clean analytics infographic"
    ]
    return generate_json(system_prompt, user_prompt, fallback)


@tool
def ab_test_versions(idea: str, tone: str) -> dict:
    """
    Generate two A/B test versions of a post.
    """
    system_prompt = "CRO copywriter creating A/B test variations."
    user_prompt = (
        f"2 A/B versions for: \"{idea[:150]}\" tone: \"{tone}\"\n"
        f"JSON: {{\"version_a\":\"...\",\"version_b\":\"...\",\"difference\":\"1 sentence\"}}"
    )
    fallback = {
        "version_a": f"Version A: {idea}",
        "version_b": f"Version B: {idea}",
        "difference": "A=logic, B=emotion"
    }
    return generate_json(system_prompt, user_prompt, fallback)