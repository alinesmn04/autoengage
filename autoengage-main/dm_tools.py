"""
Direct message tools for AutoEngage.
"""

from langchain_core.tools import tool
from pydantic import BaseModel, Field

from persistence import CONVERSATIONS, save_all


class InteractionInput(BaseModel):
    name: str = Field(description="Name of the person who interacted.")
    action: str = Field(description="The interaction action (e.g. liked, commented, asked question).")


class IdentifyWarmLeadsInput(BaseModel):
    interactions: list[InteractionInput] = Field(description="List of user interactions to analyze.")


@tool(args_schema=IdentifyWarmLeadsInput)
def identify_warm_leads(interactions: list[dict]) -> list:
    """
    Identify warm leads based on interactions.
    """

    warm_leads = []

    for person in interactions:
        score = 0
        p_action = person.action if hasattr(person, "action") else person["action"]
        p_name = person.name if hasattr(person, "name") else person["name"]

        if "commented" in p_action:
            score += 50

        if "asked question" in p_action:
            score += 30

        if "liked" in p_action:
            score += 20

        warm_leads.append({
            "name": p_name,
            "score": score,
            "reason": p_action
        })

    warm_leads.sort(key=lambda x: x["score"], reverse=True)

    return warm_leads


@tool
def draft_dm(lead_name: str, context: str, brand_tone: str) -> str:
    """
    Create a personalized DM for a lead.
    """
    from llm_helper import generate_text
    system_prompt = (
        f"You are a sales copywriter writing personalized direct messages (DMs) "
        f"to warm leads. The brand tone is: {brand_tone}."
    )
    user_prompt = (
        f"Draft a warm, personal, and conversational direct outreach message to {lead_name}.\n"
        f"Context of their interaction: \"{context}\".\n\n"
        f"Ensure it doesn't sound spammy, is helpful first, and invites them to have a conversation or download our free resource."
    )
    return generate_text(system_prompt, user_prompt)


@tool
def track_conversation(lead_name: str, message: str, status: str) -> str:
    """
    Save a conversation to memory.
    """

    conversation = {
        "lead_name": lead_name,
        "message": message,
        "status": status
    }

    CONVERSATIONS.append(conversation)
    save_all()

    print(f"Conversation saved for {lead_name}")

    return f"Conversation with '{lead_name}' tracked successfully."