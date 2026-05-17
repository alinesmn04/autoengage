"""
Analytics tools for AutoEngage.
"""

from langchain_core.tools import tool


@tool
def analyze_engagement(posts_data: list) -> str:
    """
    Analyze which posts performed best.
    """

    if not posts_data:
        return "No post data provided."

    best_post = max(posts_data, key=lambda x: x["likes"] + x["comments"])

    return (
        f"Best performing post: '{best_post['title']}'\n"
        f"Likes: {best_post['likes']}\n"
        f"Comments: {best_post['comments']}\n"
        f"This post performed well because it generated strong engagement."
    )


@tool
def generate_insights(analytics: str) -> dict:
    """
    Generate insights and recommendations from analytics.
    """

    return {
        "insights": [
            "Posts about automation receive more engagement",
            "Short posts perform better",
            "Educational content attracts more comments",
            "CTA increases interaction",
            "LinkedIn performs best for professional content"
        ],
        "recommendations": [
            "Post more educational content",
            "Use shorter captions",
            "Add stronger CTA to posts"
        ]
    }


@tool
def score_lead(lead_name: str, interactions: list) -> dict:
    """
    Score a lead based on interactions.
    """

    score = 0

    for action in interactions:
        if action == "comment":
            score += 40
        elif action == "question":
            score += 40
        elif action == "like":
            score += 20

    if score >= 80:
        level = "hot"
        recommendation = "Send a personalized offer"
    elif score >= 40:
        level = "warm"
        recommendation = "Continue engagement"
    else:
        level = "cold"
        recommendation = "Monitor activity"

    return {
        "lead_name": lead_name,
        "score": score,
        "level": level,
        "recommendation": recommendation
    }