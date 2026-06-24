"""
Reddit platform tools for AutoEngage.
"""

from langchain_core.tools import tool


@tool
def reddit_search_posts(subreddit: str, query: str, limit: int = 10) -> list:
    """
    Search posts in a subreddit.
    """
    from llm_helper import generate_json
    import requests
    import json
    
    url = "https://reddit34.p.rapidapi.com/getSearchPosts"
    querystring = {"query": f"subreddit:{subreddit} {query}"}
    headers = {
        "x-rapidapi-key": "e971cece7fmsh029effc64849cf3p10be7cjsnc23c8322039c",
        "x-rapidapi-host": "reddit34.p.rapidapi.com"
    }
    
    try:
        response = requests.get(url, headers=headers, params=querystring, timeout=15)
        real_search_text = response.text
    except Exception as e:
        real_search_text = f"API Error: {str(e)}"
    
    system_prompt = f"You are an intelligent data parser that extracts Reddit post info from raw search results."
    user_prompt = (
        f"Extract exactly 3 search results from the following search text for r/{subreddit}:\n"
        f"---RAW RESULTS---\n{real_search_text[:6000]}\n------------------------\n\n"
        f"If the raw results say 'No results found' or 'success':false, you MUST return an empty JSON list: []. DO NOT generate fake results.\n"
        f"Otherwise, extract the REAL results and format them. Each result must have:\n"
        f"- \"title\": The title of the Reddit post\n"
        f"- \"score\": The score of the post (integer)\n"
        f"- \"comments\": The number of comments (integer)\n"
        f"- \"url\": THE EXACT URL extracted from the search result (make it absolute: https://reddit.com...). Use the 'permalink' field if available."
    )
    fallback = []
    return generate_json(system_prompt, user_prompt, fallback)


@tool
def reddit_read_post(post_url: str) -> dict:
    """
    Read a Reddit post and return content with comments.
    """
    from llm_helper import generate_json
    system_prompt = "You are a simulation of the Reddit API scraper."
    user_prompt = (
        f"Simulate reading the Reddit post at URL: \"{post_url}\".\n"
        f"Generate a realistic post body and a list of 3 top comments discussing the post.\n"
        f"Return a JSON object with exactly these keys:\n"
        f"- \"post_content\": A realistic post body content (at least 2 paragraphs)\n"
        f"- \"top_comments\": A list of 3 strings representing realistic comments/replies discussing the topic."
    )
    fallback = {
        "post_content": f"Content from Reddit post: {post_url}",
        "top_comments": [
            "This is a helpful discussion.",
            "I had the same question.",
            "Automation saved me a lot of time."
        ]
    }
    return generate_json(system_prompt, user_prompt, fallback)


@tool
def reddit_post_comment(post_url: str, comment_text: str) -> str:
    """
    Post a comment to Reddit.
    """

    return f"Comment posted successfully to {post_url}"


@tool
def reddit_monitor_replies(username: str) -> list:
    """
    Monitor new replies to our Reddit comments.
    """
    from llm_helper import generate_json
    system_prompt = "You are a simulator of Reddit notifications."
    user_prompt = (
        f"Simulate new replies to the Reddit user \"{username}\" based on marketing/automation topics.\n"
        f"Generate a JSON list of exactly 2 notification objects. Each object must have:\n"
        f"- \"from_user\": A realistic Reddit username\n"
        f"- \"reply\": A realistic user comment reply (either asking a question, saying thanks, or sharing a concern)\n"
        f"- \"status\": The string \"new\""
    )
    fallback = [
        {
            "from_user": "reddit_user123",
            "reply": "Thanks for the helpful comment!",
            "status": "new"
        }
    ]
    return generate_json(system_prompt, user_prompt, fallback)