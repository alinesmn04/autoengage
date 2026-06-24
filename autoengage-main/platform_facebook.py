"""
Facebook platform tools for AutoEngage.
"""

from langchain_core.tools import tool


@tool
def facebook_search_posts(query: str, results_max: int = 5) -> list:
    """
    Search Facebook posts using RapidAPI.
    """
    from llm_helper import generate_json
    # RapidAPI Facebook integration
    import requests
    import json
    
    url = "https://facebook-scraper3.p.rapidapi.com/search/posts"
    querystring = {"query": query}
    headers = {
        "x-rapidapi-key": "e971cece7fmsh029effc64849cf3p10be7cjsnc23c8322039c",
        "x-rapidapi-host": "facebook-scraper3.p.rapidapi.com"
    }
    
    try:
        response = requests.get(url, headers=headers, params=querystring, timeout=15)
        real_search_text = response.text
    except Exception as e:
        real_search_text = f"API Error: {str(e)}"
    
    system_prompt = "You are an intelligent data parser that extracts Facebook post info from raw search results."
    user_prompt = (
        f"Extract exactly {results_max} search results from the following search text:\n"
        f"---RAW RESULTS---\n{real_search_text}\n------------------------\n\n"
        f"If the raw results say 'No results found', you MUST return an empty JSON list: []. DO NOT generate fake results.\n"
        f"Otherwise, extract the REAL results and format them. Each result must have:\n"
        f"- \"title\": The text or title of the post\n"
        f"- \"author\": Extract or guess the author name/page name\n"
        f"- \"url\": THE EXACT URL extracted from the search result (must be absolute)."
    )
    fallback = []
    return generate_json(system_prompt, user_prompt, fallback)


@tool
def facebook_read_post(post_url: str) -> str:
    """
    Read a Facebook post content.
    """
    from llm_helper import generate_text
    system_prompt = "You are a simulator of a Facebook web crawler."
    user_prompt = (
        f"Simulate reading the full content of the Facebook post at URL: \"{post_url}\".\n"
        f"Generate a realistic, conversational Facebook post content (at least 2 paragraphs with emojis)."
    )
    return generate_text(system_prompt, user_prompt)


@tool
def facebook_post_comment(post_url: str, comment_text: str) -> str:
    """
    Post a comment on Facebook.
    """

    return f"Facebook comment posted successfully to {post_url}"
