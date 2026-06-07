"""
Content creation tools for AutoEngage.
"""

from langchain_core.tools import tool
from llm_helper import generate_text, generate_json


@tool
def generate_post_ideas(niche: str, count: int = 5) -> list:
    """
    Generate numbered post ideas for a niche.
    """
    system_prompt = "You are a creative social media manager brainstorming content ideas."
    user_prompt = f"Brainstorm {count} high-engagement social media post ideas for the niche: {niche}. Return them as a JSON list of strings."
    fallback = [f"How {niche} can improve productivity"] * count
    return generate_json(system_prompt, user_prompt, fallback)


@tool
def write_post(idea: str, platform: str, tone: str) -> str:
    """
    Generate a social media post adapted to a platform.
    """
    system_prompt = (
        f"You are a professional copywriter. Write a post for the platform: {platform} "
        f"using the tone: {tone}."
    )
    user_prompt = (
        f"Draft a complete post about this idea:\n\"{idea}\"\n\n"
        f"Ensure it follows platform best practices (e.g. hashtags and structured spacing for LinkedIn, "
        f"conversational and detailed for Reddit, short and punchy within 280 chars for Twitter)."
    )
    res = generate_text(system_prompt, user_prompt)
    if not res:
        res = f"Here is our take on: {idea}. Success starts with clear goals and smart execution. Let's make it happen! #{platform} #success"
    return res


@tool
def suggest_visual(post_text: str) -> list:
    """
    Suggest visual ideas for a post.
    """
    system_prompt = "You are a creative art director suggesting visuals for social media posts."
    user_prompt = (
        f"Read this post content:\n\"{post_text}\"\n\n"
        f"Suggest exactly 3 visual ideas (images, infographics, diagrams, or video concepts) "
        f"that would complement this post. Return them as a JSON list of strings."
    )
    fallback = [
        "Modern office workspace with AI dashboard",
        "Small business owner using automation tools",
        "Minimal social media infographic with analytics"
    ]
    return generate_json(system_prompt, user_prompt, fallback)


@tool
def ab_test_versions(idea: str, tone: str) -> dict:
    """
    Generate two A/B test versions of a post.
    """
    system_prompt = "You are a conversion rate optimization (CRO) expert."
    user_prompt = (
        f"Create two A/B test versions of a social media post for this idea: \"{idea}\" "
        f"using the brand tone \"{tone}\".\n\n"
        f"Return a JSON object with these keys:\n"
        f"- \"version_a\": The full text of version A (e.g. focusing on logic, hooks, or direct value)\n"
        f"- \"version_b\": The full text of version B (e.g. focusing on storytelling, emotion, or curiosity)\n"
        f"- \"difference\": A short description of the difference in approach between A and B."
    )
    fallback = {
        "version_a": f"Version A: {idea}",
        "version_b": f"Version B: {idea}",
        "difference": "A focuses on logic, B focuses on emotion."
    }
    return generate_json(system_prompt, user_prompt, fallback)