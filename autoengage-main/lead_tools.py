"""
Lead magnet tools for AutoEngage.
"""

from langchain_core.tools import tool
from fpdf import FPDF

# Simple in-memory lead storage
LEADS = []


@tool
def create_lead_magnet_outline(topic: str, target_audience: str) -> dict:
    """
    Create a lead magnet outline with 5 chapters.
    """

    outline = {
        "title": f"The Ultimate Guide to {topic}",
        "chapters": [
            {"title": "Introduction", "summary": f"Why {topic} matters today"},
            {"title": "Common Problems", "summary": f"Challenges faced by {target_audience}"},
            {"title": "Best Strategies", "summary": f"Top ways to improve using {topic}"},
            {"title": "Tools and Automation", "summary": "Helpful tools and systems"},
            {"title": "Action Plan", "summary": "Step-by-step implementation guide"}
        ]
    }

    return outline


@tool
def generate_lead_magnet_pdf(title: str, chapters: list, filename: str) -> str:
    """
    Generate a PDF lead magnet file.
    """

    pdf = FPDF()
    pdf.add_page()

    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, title, ln=True)

    pdf.ln(10)

    pdf.set_font("Arial", size=12)

    for chapter in chapters:
        pdf.cell(0, 10, chapter["title"], ln=True)
        pdf.multi_cell(0, 10, chapter["summary"])
        pdf.ln(5)

    pdf.output(filename)

    return f"PDF generated successfully: {filename}"


@tool
def write_cta_for_lead_magnet(magnet_title: str, platform: str) -> list:
    """
    Generate CTA variations for a lead magnet.
    """

    return [
        f"Download our free guide: {magnet_title}",
        f"Comment GUIDE to get '{magnet_title}'",
        f"Get instant access to '{magnet_title}' today"
    ]


@tool
def capture_lead(username: str, platform: str, interest: str) -> str:
    """
    Save a lead to memory.
    """

    lead = {
        "username": username,
        "platform": platform,
        "interest": interest
    }

    LEADS.append(lead)

    print(f"Lead saved: {username}")

    return f"Lead '{username}' saved successfully."