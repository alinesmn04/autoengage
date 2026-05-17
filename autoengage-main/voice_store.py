"""
Voice store tools for AutoEngage.
This module stores and searches writing style samples.
"""

from langchain_core.tools import tool

# Simple in-memory voice samples storage
VOICE_SAMPLES = []


@tool
def add_voice_sample(text: str, category: str) -> str:
    """
    Save a writing style sample.
    """

    sample = {
        "text": text,
        "category": category
    }

    VOICE_SAMPLES.append(sample)

    return f"Voice sample saved successfully in category: {category}"


@tool
def find_similar_voice(query: str, category: str, k: int = 3) -> list:
    """
    Find similar writing samples by category.
    """

    results = []

    for sample in VOICE_SAMPLES:
        if sample["category"] == category:
            results.append(sample)

    return results[:k]