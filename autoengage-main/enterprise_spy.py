import json
from langchain_core.tools import tool
from playwright.sync_api import sync_playwright
from llm_helper import generate_text

@tool
def monitor_competitor_website(competitor_url: str) -> str:
    """
    Scrape a competitor's website to extract their core messaging and recent updates.
    """
    try:
        if not competitor_url.startswith("http"):
            competitor_url = "https://" + competitor_url
            
        with sync_playwright() as p:
            browser = p.firefox.launch(headless=True)
            context = browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            )
            page = context.new_page()
            page.goto(competitor_url, wait_until="domcontentloaded", timeout=15000)
            
            title = page.title()
            
            # Extract main readable text
            body_text = page.locator("body").inner_text()
            
            browser.close()
            
            result = {
                "competitor_url": competitor_url,
                "title": title,
                "content_preview": body_text[:2000] # Limit tokens
            }
            return json.dumps(result, ensure_ascii=False, indent=2)
    except Exception as e:
        return f"Error monitoring competitor: {str(e)}"

@tool
def extract_competitor_strategy(competitor_content: str) -> str:
    """
    Analyze the competitor's website content to extract their marketing strategy and value proposition.
    """
    system_prompt = "You are an Elite Enterprise Competitive Intelligence Agent. Provide all output in Hebrew."
    user_prompt = (
        f"Analyze this competitor's website content:\n{competitor_content}\n\n"
        f"Extract their core marketing strategy. What is their main value proposition? "
        f"Identify 3 major weaknesses or 'holes' in their offering that our company can exploit. "
        f"IMPORTANT: Write the entire analysis in professional Hebrew."
    )
    return generate_text(system_prompt, user_prompt)

@tool
def generate_counter_campaign(competitor_name: str, findings: str) -> str:
    """
    Generate an aggressive counter-campaign based on the competitor's weaknesses.
    """
    system_prompt = "You are a ruthless CMO. Write compelling Hebrew marketing copy."
    user_prompt = (
        f"Competitor Name: {competitor_name}\n"
        f"Competitor Weaknesses and Findings:\n{findings}\n\n"
        f"Generate a 'Counter-Campaign'. Write 3 different LinkedIn post variations that implicitly target these exact weaknesses without explicitly naming the competitor (e.g. 'Tired of platforms that do X? We do Y.').\n"
        f"IMPORTANT: Write the posts in high-quality Hebrew."
    )
    return generate_text(system_prompt, user_prompt)
