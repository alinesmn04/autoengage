"""
Lead magnet tools for AutoEngage.
"""

from langchain_core.tools import tool
from pydantic import BaseModel, Field
from fpdf import FPDF

# Simple in-memory lead storage
from persistence import LEADS, save_all


class PremiumPDF(FPDF):
    def __init__(self, brand_name="AutoEngage", title="Premium Marketing Guide", *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.brand_name = brand_name
        self.doc_title = title

    def header(self):
        # Header only on page 2 and later
        if self.page_no() > 1:
            self.set_font("Arial", "I", 9)
            self.set_text_color(100, 116, 139) # slate-500
            self.cell(0, 10, f"{self.brand_name}  |  {self.doc_title}", 0, 0, "L")
            self.set_draw_color(226, 232, 240) # slate-200
            self.line(10, 18, 200, 18)
            self.ln(10)

    def footer(self):
        # Footer only on page 2 and later
        if self.page_no() > 1:
            self.set_y(-15)
            self.set_font("Arial", "I", 9)
            self.set_text_color(148, 163, 184) # slate-400
            self.cell(0, 10, f"Page {self.page_no()}", 0, 0, "C")


@tool
def create_lead_magnet_outline(topic: str, target_audience: str) -> dict:
    """
    Create a lead magnet outline with 5 chapters.
    """
    from llm_helper import generate_json
    system_prompt = "You are a content strategist designing premium Lead Magnets."
    user_prompt = (
        f"Create a high-value Lead Magnet outline for this topic: \"{topic}\"\n"
        f"Target audience: {target_audience}\n\n"
        f"Return a JSON object with exactly these keys:\n"
        f"- \"title\": A creative, high-converting title for the guide/PDF\n"
        f"- \"chapters\": A list of exactly 5 dictionaries. Each dictionary must have:\n"
        f"  * \"title\": Chapter title\n"
        f"  * \"summary\": Detailed summary of what is covered in this chapter."
    )
    fallback = {
        "title": f"The Ultimate Guide to {topic}",
        "chapters": [
            {"title": "Introduction", "summary": f"Why {topic} matters today"},
            {"title": "Common Problems", "summary": f"Challenges faced by {target_audience}"},
            {"title": "Best Strategies", "summary": f"Top ways to improve using {topic}"},
            {"title": "Tools and Automation", "summary": "Helpful tools and systems"},
            {"title": "Action Plan", "summary": "Step-by-step implementation guide"}
        ]
    }
    return generate_json(system_prompt, user_prompt, fallback)


class ChapterInput(BaseModel):
    title: str = Field(description="Title of the chapter.")
    summary: str = Field(description="Summary or content of the chapter.")


class GenerateLeadMagnetPdfInput(BaseModel):
    title: str = Field(description="Title of the lead magnet.")
    chapters: list[ChapterInput] = Field(description="List of chapters, each containing a title and summary.")
    filename: str = Field(description="Output filename/path for the generated PDF.")


@tool(args_schema=GenerateLeadMagnetPdfInput)
def generate_lead_magnet_pdf(title: str, chapters: list[dict], filename: str) -> str:
    """
    Generate a beautifully styled PDF lead magnet file.
    """
    from brand_profile import BRAND

    brand_name = BRAND.get("name", "AutoEngage")
    website = BRAND.get("website", "https://autoengage.ai")

    # Initialize premium PDF helper
    pdf = PremiumPDF(brand_name=brand_name, title=title)
    
    # ------------------ COVER PAGE ------------------
    pdf.add_page()
    
    # Decorative Header Band (Deep Indigo)
    pdf.set_fill_color(79, 70, 229) # indigo-600
    pdf.rect(0, 0, 210, 80, "F")
    
    # Title of PDF inside/below the band
    pdf.set_y(35)
    pdf.set_font("Arial", "B", 26)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(0, 12, brand_name.upper(), ln=True, align="C")
    
    pdf.set_font("Arial", size=14)
    pdf.set_text_color(224, 231, 255) # indigo-100
    pdf.cell(0, 10, "PREMIUM MARKETING INSIGHTS", ln=True, align="C")
    
    # Rest of cover page
    pdf.set_y(100)
    pdf.set_font("Arial", "B", 20)
    pdf.set_text_color(30, 41, 59) # slate-800
    pdf.multi_cell(0, 10, title, align="C")
    
    # Center accent divider line
    pdf.set_draw_color(99, 102, 241) # indigo-500
    pdf.line(75, 140, 135, 140)
    
    # Footer metadata on Cover Page
    pdf.set_y(220)
    pdf.set_font("Arial", "B", 11)
    pdf.set_text_color(79, 70, 229)
    pdf.cell(0, 6, "Prepared for Our Valued Community", ln=True, align="C")
    
    pdf.set_font("Arial", size=10)
    pdf.set_text_color(100, 116, 139)
    pdf.cell(0, 6, f"Published Autonomously by {brand_name} AI", ln=True, align="C")
    pdf.cell(0, 6, f"Learn more: {website}", ln=True, align="C")
    
    # ------------------ CONTENT PAGES ------------------
    pdf.add_page()
    pdf.set_text_color(51, 65, 85) # slate-700
    
    for idx, chapter in enumerate(chapters):
        ch_title = chapter.title if hasattr(chapter, "title") else chapter["title"]
        ch_summary = chapter.summary if hasattr(chapter, "summary") else chapter["summary"]
        
        # Start new page if spacing is tight, except for first chapter
        if idx > 0 and pdf.get_y() > 180:
            pdf.add_page()
            
        # Chapter header
        pdf.set_font("Arial", "B", 14)
        pdf.set_text_color(79, 70, 229) # Indigo
        pdf.cell(0, 10, f"Chapter {idx+1}: {ch_title}", ln=True)
        
        # Underline accent
        pdf.set_draw_color(226, 232, 240)
        pdf.line(10, pdf.get_y(), 200, pdf.get_y())
        pdf.ln(5)
        
        # Chapter Body Text
        pdf.set_font("Arial", size=10.5)
        pdf.set_text_color(51, 65, 85) # Slate-700
        pdf.multi_cell(0, 7, ch_summary)
        pdf.ln(8)
        
    # ------------------ CALL TO ACTION (CTA) SECTION ------------------
    if pdf.get_y() > 190:
        pdf.add_page()
        
    pdf.ln(10)
    pdf.set_fill_color(248, 250, 252) # slate-50
    pdf.set_draw_color(226, 232, 240) # slate-200
    pdf.rect(10, pdf.get_y(), 190, 40, "DF")
    
    pdf.set_y(pdf.get_y() + 5)
    pdf.set_x(15)
    pdf.set_font("Arial", "B", 12)
    pdf.set_text_color(79, 70, 229)
    pdf.cell(0, 6, f"Ready to Automate Your Brand Success?", ln=True)
    
    pdf.set_x(15)
    pdf.set_font("Arial", size=10)
    pdf.set_text_color(71, 85, 105)
    pdf.multi_cell(180, 5, f"This document was fully researched and compiled by {brand_name}'s autonomous marketing agents. If you'd like to unlock more productivity, scale engagement, and capture warm leads on autopilot, let's connect!")
    
    pdf.ln(2)
    pdf.set_x(15)
    pdf.set_font("Arial", "B", 10)
    pdf.set_text_color(79, 70, 229)
    pdf.cell(0, 6, f"Get started today at: {website}", ln=True)

    pdf.output(filename)

    return f"PDF generated successfully: {filename}"


@tool
def write_cta_for_lead_magnet(magnet_title: str, platform: str) -> list:
    """
    Generate CTA variations for a lead magnet.
    """
    from llm_helper import generate_json
    system_prompt = "You are a copywriter specialized in writing high-converting calls to action."
    user_prompt = (
        f"Write exactly 3 distinct, high-converting calls to action (CTAs) for a lead magnet titled \"{magnet_title}\" "
        f"to be shared on the platform: {platform}.\n"
        f"Return them as a JSON list of strings."
    )
    fallback = [
        f"Download our free guide: {magnet_title}",
        f"Comment GUIDE to get '{magnet_title}'",
        f"Get instant access to '{magnet_title}' today"
    ]
    return generate_json(system_prompt, user_prompt, fallback)


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
    save_all()

    print(f"Lead saved: {username}")

    return f"Lead '{username}' saved successfully."