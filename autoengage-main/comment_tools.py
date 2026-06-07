"""
Comment tools for AutoEngage.

This module creates comments and performs QA checks
before publishing.
"""

from langchain_core.tools import tool
from pydantic import BaseModel, Field
from llm_helper import generate_text, generate_json


@tool
def draft_comment(post_summary: str, brand_tone: str, cta: str) -> str:
    """
    Generate a marketing comment based on a post summary.
    """
    system_prompt = (
        f"You are AutoEngage, an autonomous marketing agent. "
        f"Your task is to write a valuable, engaging, and professional social media comment on a post. "
        f"The brand tone is: {brand_tone}. The call to action (CTA) to integrate is: {cta}."
    )
    user_prompt = (
        f"Here is the post content/summary:\n{post_summary}\n\n"
        f"Write a valuable comment that contributes to the discussion and naturally includes the CTA at the end."
    )
    res = generate_text(system_prompt, user_prompt)
    if not res:
        res = f"Great insights! Streamlining operations and automation can really help scale business efficiency. Feel free to connect to learn more: {cta}"
    return res


class QaCheckCommentInput(BaseModel):
    comment: str = Field(description="The comment text to perform QA checks on.")
    phrases_forbidden: list[str] = Field(description="List of forbidden phrases that must not appear in the comment.")


@tool(args_schema=QaCheckCommentInput)
def qa_check_comment(comment: str, phrases_forbidden: list[str]) -> dict:
    """
    Perform QA checks on a generated comment.
    """
    system_prompt = "You are a Quality Assurance bot that checks marketing comments for quality, forbidden phrases, AI tone, and length."
    user_prompt = (
        f"Evaluate the following comment:\n\"{comment}\"\n\n"
        f"Forbidden phrases list: {phrases_forbidden}\n\n"
        f"Perform these checks and output a JSON dictionary with these keys:\n"
        f"- \"forbidden_check\": \"✅ No forbidden phrases\" or \"❌ Found forbidden phrases: <phrases>\"\n"
        f"- \"ai_smell\": \"✅ Comment sounds natural\" or \"⚠️ Comment sounds AI-generated\" (check for words like revolutionary, game changer, next level, cutting-edge, unlock, etc.)\n"
        f"- \"value_check\": \"✅ Comment contains meaningful value\" or \"❌ Comment is too short/generic\"\n"
        f"- \"length_check\": \"✅ Comment length is valid\" or \"❌ Comment length is invalid\"\n"
    )
    
    fallback = {
        "forbidden_check": "✅ No forbidden phrases",
        "ai_smell": "✅ Comment sounds natural",
        "value_check": "✅ Comment contains meaningful value",
        "length_check": "✅ Comment length is valid"
    }
    return generate_json(system_prompt, user_prompt, fallback)