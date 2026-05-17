"""
Content creation tools for AutoEngage.
"""

from langchain_core.tools import tool


@tool
def generate_post_ideas(niche: str, count: int = 5) -> list:
    """
    Generate numbered post ideas for a niche.
    """

    ideas = []

    for i in range(count):
        ideas.append(f"{i+1}. How {niche} can improve productivity")

    return ideas


@tool
def write_post(idea: str, platform: str, tone: str) -> str:
    """
    Generate a social media post adapted to a platform.
    """

    platform = platform.lower()

    if platform == "linkedin":
        return (
            f"🚀 {idea}\n\n"
            f"Businesses that adopt automation early gain a major advantage.\n\n"
            f"#AI #BusinessGrowth"
        )

    elif platform == "reddit":
        return (
            f"I've been thinking a lot about this lately:\n\n"
            f"{idea}\n\n"
            f"Curious if anyone here had similar experiences."
        )

    elif platform == "twitter":
        return (
            f"{idea} 🚀\n"
            f"Automation is changing everything. #AI"
        )[:280]

    else:
        return "Unsupported platform."


@tool
def suggest_visual(post_text: str) -> list:
    """
    Suggest visual ideas for a post.
    """

    return [
        "Modern office workspace with AI dashboard",
        "Small business owner using automation tools",
        "Minimal social media infographic with analytics"
    ]


@tool
def ab_test_versions(idea: str, tone: str) -> dict:
    """
    Generate two A/B test versions of a post.
    """

    version_a = (
        f"Version A:\n"
        f"{idea}\n"
        f"Focus on productivity and efficiency."
    )

    version_b = (
        f"Version B:\n"
        f"{idea}\n"
        f"Focus on business growth and customer experience."
    )

    return {
        "version_a": version_a,
        "version_b": version_b,
        "difference": "A focuses on productivity, B focuses on growth."
    }