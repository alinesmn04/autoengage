"""
Analytics tools for AutoEngage.
"""

from langchain_core.tools import tool
from pydantic import BaseModel, Field


class PostDataInput(BaseModel):
    title: str = Field(description="Title or content summary of the post")
    likes: int = Field(description="Number of likes")
    comments: int = Field(description="Number of comments")


class AnalyzeEngagementInput(BaseModel):
    posts_data: list[PostDataInput] = Field(description="List of posts to analyze.")


@tool(args_schema=AnalyzeEngagementInput)
def analyze_engagement(posts_data: list[dict]) -> str:
    """
    Analyze which posts performed best.
    """

    if not posts_data:
        return "No post data provided."

    def get_metric(x, key):
        return x.get(key) if isinstance(x, dict) else getattr(x, key, 0)

    best_post = max(posts_data, key=lambda x: get_metric(x, "likes") + get_metric(x, "comments"))

    best_title = get_metric(best_post, "title")
    best_likes = get_metric(best_post, "likes")
    best_comments = get_metric(best_post, "comments")

    return (
        f"Best performing post: '{best_title}'\n"
        f"Likes: {best_likes}\n"
        f"Comments: {best_comments}\n"
        f"This post performed well because it generated strong engagement."
    )


@tool
def generate_insights(analytics: str) -> dict:
    """
    Generate insights and recommendations from analytics.
    """
    from llm_helper import generate_json
    system_prompt = "You are a senior marketing analyst."
    user_prompt = (
        f"Based on the following engagement analysis report:\n{analytics}\n\n"
        f"Generate a JSON object with exactly these keys:\n"
        f"- \"insights\": A list of 5 detailed analytical findings/observations.\n"
        f"- \"recommendations\": A list of 3 actionable strategic suggestions/recommendations to improve performance."
    )
    fallback = {
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
    return generate_json(system_prompt, user_prompt, fallback)


class ScoreLeadInput(BaseModel):
    lead_name: str = Field(description="Name of the lead to score.")
    interactions: list[str] = Field(description="List of interaction types/actions (e.g. comment, question, like).")


@tool(args_schema=ScoreLeadInput)
def score_lead(lead_name: str, interactions: list[str]) -> dict:
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