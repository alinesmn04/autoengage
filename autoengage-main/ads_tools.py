"""
Advertising research tools for AutoEngage.
"""

from langchain_core.tools import tool


@tool
def research_competitor_ads(competitor_name: str) -> str:
    """
    Analyze competitor advertising style.
    """

    return (
        f"Competitor '{competitor_name}' focuses on:\n"
        f"- Simple messaging\n"
        f"- Strong CTA\n"
        f"- Automation benefits\n"
        f"- Customer pain points\n"
        f"- Short and engaging ad copy"
    )


@tool
def extract_ad_patterns(data_ads: str) -> list:
    """
    Extract common advertising patterns.
    """

    return [
        "Use emotional hooks",
        "Short CTA sentences",
        "Focus on customer problems",
        "Highlight time-saving benefits",
        "Use simple language"
    ]


@tool
def suggest_ad_copy(patterns: str, brand_tone: str) -> list:
    """
    Generate ad copy ideas based on ad patterns.
    """

    return [
        "Save hours every week with smart AI automation.",
        "Your business deserves simpler workflows and faster results.",
        "Automate repetitive tasks and focus on growth."
    ]