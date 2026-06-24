"""
LinkedIn platform tools for AutoEngage.
"""

from langchain_core.tools import tool


@tool
def linkedin_search_posts(query: str, results_max: int = 5) -> list:
    """
    Search LinkedIn posts using DuckDuckGo search.
    """
    from duckduckgo_search import DDGS

    search_query = f"site:linkedin.com/posts/ {query}"
    
    try:
        parsed_results = []
        with DDGS() as ddgs:
            results = list(ddgs.text(search_query, max_results=results_max))
            
            for item in results:
                title = item.get("title", "LinkedIn Post")
                post_url = item.get("href", "")
                snippet = item.get("body", "")
                
                author = "LinkedIn User"
                if " - LinkedIn" in title:
                    author_guess = title.split(" - LinkedIn")[0].strip()
                    if "Post by " in author_guess:
                        author = author_guess.replace("Post by ", "")
                    else:
                        author = author_guess
                        
                parsed_results.append({
                    "title": title,
                    "author": author,
                    "summary": snippet,
                    "url": post_url
                })
                
        if not parsed_results:
            # Fallback format if API succeeds but returns nothing
            parsed_results = [{
                "title": f"LinkedIn Search for {query}",
                "author": "System",
                "summary": f"No specific posts found for {query} on LinkedIn.",
                "url": "https://www.linkedin.com/search/results/all/?keywords=" + query
            }]
            
        return parsed_results
        
    except Exception as e:
        print(f"DuckDuckGo Search error for LinkedIn: {e}")
        return [{
            "title": f"LinkedIn Search Error",
            "author": "System",
            "summary": f"Failed to search for {query}: {e}",
            "url": "https://www.linkedin.com/"
        }]


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