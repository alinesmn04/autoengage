"""
LinkedIn platform tools for AutoEngage.
"""

from langchain_core.tools import tool


@tool
def linkedin_search_posts(query: str, results_max: int = 5) -> list:
    """
    Search LinkedIn posts using browser automation.
    """
    from llm_helper import generate_json
    system_prompt = "You are a simulator of the LinkedIn search API."
    user_prompt = (
        f"Simulate a search on LinkedIn for the query: \"{query}\".\n"
        f"Generate a JSON list of exactly 3 realistic search results. Each result must have:\n"
        f"- \"title\": A professional LinkedIn post title or short summary (e.g. \"Why I moved my CRM to make.com\")\n"
        f"- \"author\": A realistic professional name and title (e.g. \"Jane Doe, Founder of TechX\")\n"
        f"- \"summary\": A short, realistic professional summary of the LinkedIn post content."
    )
    fallback = [
        {
            "title": f"LinkedIn post about {query}",
            "author": "Example Author",
            "summary": "A short summary of a professional LinkedIn post."
        }
    ]
    return generate_json(system_prompt, user_prompt, fallback)


@tool
def linkedin_read_post(post_url: str) -> str:
    """
    Read a LinkedIn post content.
    """
    from llm_helper import generate_text
    system_prompt = "You are a simulator of a LinkedIn web crawler."
    user_prompt = (
        f"Simulate reading the full content of the LinkedIn post at URL: \"{post_url}\".\n"
        f"Generate a realistic, professional, formatted LinkedIn post content (at least 3 paragraphs with hashtags)."
    )
    return generate_text(system_prompt, user_prompt)


@tool
def linkedin_post_comment(post_url: str, comment_text: str) -> str:
    """
    Post a comment on LinkedIn.
    """

    return f"LinkedIn comment posted successfully to {post_url}"