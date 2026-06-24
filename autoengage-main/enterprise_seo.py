import json
from langchain_core.tools import tool
from playwright.sync_api import sync_playwright
from llm_helper import generate_text

@tool
def scan_website_seo(url: str) -> str:
    """
    Scan a website and extract SEO metrics: Title, Meta Description, H1s, H2s, and main text.
    """
    try:
        if not url.startswith("http"):
            url = "https://" + url
            
        with sync_playwright() as p:
            browser = p.firefox.launch(headless=True)
            context = browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            )
            page = context.new_page()
            page.goto(url, wait_until="domcontentloaded", timeout=15000)
            
            title = page.title()
            desc_loc = page.locator("meta[name='description']")
            meta_desc = desc_loc.first.get_attribute("content") if desc_loc.count() > 0 else "None"
            
            h1s = [el.inner_text().strip() for el in page.locator("h1").all() if el.inner_text().strip()]
            h2s = [el.inner_text().strip() for el in page.locator("h2").all() if el.inner_text().strip()]
            
            body_text = page.locator("body").inner_text()
            
            browser.close()
            
            result = {
                "url": url,
                "title": title,
                "meta_description": meta_desc,
                "h1": h1s,
                "h2": h2s[:5],
                "content_preview": body_text[:1500]
            }
            return json.dumps(result, ensure_ascii=False, indent=2)
    except Exception as e:
        return f"Error scanning website: {str(e)}"

@tool
def analyze_seo_gaps(current_seo_data: str, target_keywords: str) -> str:
    """
    Analyze the current SEO data against target keywords and find gaps.
    """
    system_prompt = "You are an Enterprise SEO expert. You must provide all analysis and reports entirely in Hebrew."
    user_prompt = (
        f"Analyze this website's current SEO data:\n{current_seo_data}\n\n"
        f"Target Keywords: {target_keywords}\n\n"
        f"Identify the missing keywords, weak headers, and missing meta tags. "
        f"Provide a structured actionable report of the exact gaps to be filled. "
        f"IMPORTANT: Write the entire report in Hebrew."
    )
    return generate_text(system_prompt, user_prompt)

@tool
def generate_remediated_html(url: str, seo_gaps: str) -> str:
    """
    Generate fully rewritten, SEO-optimized HTML code (headers and meta) based on the identified gaps.
    """
    system_prompt = "You are an Enterprise SEO Technical Writer and Web Developer. You write excellent Hebrew marketing copy."
    user_prompt = (
        f"Based on the SEO gaps identified for {url}:\n{seo_gaps}\n\n"
        f"Write a clean, remediated HTML snippet containing the optimized <head> (title, meta description) "
        f"and the optimized <body> structure (H1, H2s) with compelling copy that fills the keyword gaps.\n"
        f"IMPORTANT: The copy inside the HTML (titles, headers, description) MUST be written in Hebrew.\n"
        f"Output ONLY the HTML block."
    )
    return generate_text(system_prompt, user_prompt)

@tool
def calculate_seo_score(current_seo_data: str) -> str:
    """
    Calculate an SEO score out of 100 based on the current metrics.
    """
    system_prompt = "You are an Enterprise SEO Scoring Engine. Output ONLY a raw JSON object with no markdown and no explanation."
    user_prompt = (
        f"Analyze this website's current SEO data:\n{current_seo_data}\n\n"
        f"Calculate a score out of 100 for the following categories based on standard SEO best practices (title length, meta description presence, h1 presence, etc):\n"
        f"1. overall\n"
        f"2. keywords\n"
        f"3. meta\n"
        f"4. structure\n\n"
        f"Output format:\n"
        f"{{\n"
        f"  \"overall\": 85,\n"
        f"  \"keywords\": 70,\n"
        f"  \"meta\": 90,\n"
        f"  \"structure\": 80\n"
        f"}}"
    )
    return generate_text(system_prompt, user_prompt)
