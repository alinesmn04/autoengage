"""
Direct message tools for AutoEngage.
"""

from langchain_core.tools import tool

# Simple conversation storage
CONVERSATIONS = []


@tool
def identify_warm_leads(interactions: list) -> list:
    """
    Identify warm leads based on interactions.
    """

    warm_leads = []

    for person in interactions:
        score = 0

        if "commented" in person["action"]:
            score += 50

        if "asked question" in person["action"]:
            score += 30

        if "liked" in person["action"]:
            score += 20

        warm_leads.append({
            "name": person["name"],
            "score": score,
            "reason": person["action"]
        })

    warm_leads.sort(key=lambda x: x["score"], reverse=True)

    return warm_leads


@tool
def draft_dm(lead_name: str, context: str, brand_tone: str) -> str:
    """
    Create a personalized DM for a lead.
    """

    return (
        f"Hey {lead_name},\n\n"
        f"I noticed that you {context}. "
        f"I thought you might enjoy some practical AI automation ideas "
        f"that could help your business.\n\n"
        f"Happy to share more if you're interested 😊"
    )


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

    print(f"Conversation saved for {lead_name}")

    return f"Conversation with '{lead_name}' tracked successfully."