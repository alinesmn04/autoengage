import json
from langchain_core.tools import tool
from llm_helper import generate_text

@tool
def generate_ab_variations(base_topic: str, audience: str, platform: str) -> str:
    """
    Generate 3 distinct marketing variations (A/B/C) for a given topic, tailored for a specific audience and platform.
    """
    system_prompt = "You are a world-class Conversion Rate Optimization (CRO) expert and copywriter. Output MUST be valid JSON only. Do not wrap in markdown code blocks."
    user_prompt = (
        f"Topic / Goal: {base_topic}\n"
        f"Target Audience: {audience}\n"
        f"Platform: {platform}\n\n"
        f"Create 3 distinct copywriting variations to test. They should have completely different psychological angles (e.g., Fear of Missing Out, Logical/Data-driven, Emotional/Story-driven).\n"
        f"IMPORTANT: Write the copy in Hebrew.\n\n"
        f"Output EXACTLY this JSON structure:\n"
        f"[\n"
        f"  {{\"id\": \"A\", \"angle\": \"FOMO\", \"copy\": \"...\"}},\n"
        f"  {{\"id\": \"B\", \"angle\": \"Logical\", \"copy\": \"...\"}},\n"
        f"  {{\"id\": \"C\", \"angle\": \"Emotional\", \"copy\": \"...\"}}\n"
        f"]"
    )
    return generate_text(system_prompt, user_prompt)

@tool
def predict_ab_performance(variations_json: str) -> str:
    """
    Analyze the 3 variations and predict their performance, scoring each out of 100 based on marketing psychology.
    """
    system_prompt = "You are an AI Predictive Marketing Engine. Output MUST be valid JSON only. Do not wrap in markdown code blocks."
    user_prompt = (
        f"Analyze these A/B/C variations:\n{variations_json}\n\n"
        f"Predict their Conversion Rate (CVR) out of 100 based on copywriting impact, clarity, and psychological triggers.\n"
        f"Provide a brief Hebrew explanation (rationale) for each score.\n\n"
        f"Output EXACTLY this JSON structure:\n"
        f"[\n"
        f"  {{\"id\": \"A\", \"score\": 85, \"rationale\": \"...\"}},\n"
        f"  {{\"id\": \"B\", \"score\": 72, \"rationale\": \"...\"}},\n"
        f"  {{\"id\": \"C\", \"score\": 90, \"rationale\": \"...\"}}\n"
        f"]"
    )
    return generate_text(system_prompt, user_prompt)
