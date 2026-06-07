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
    system_prompt = f"You are a simulation of the Reddit search API for r/{subreddit}."
    user_prompt = (
        f"Simulate a search in r/{subreddit} for the query: \"{query}\".\n"
        f"Generate a JSON list of exactly 3 realistic search results. Each result must have:\n"
        f"- \"title\": A realistic Reddit post title related to the query\n"
        f"- \"score\": An integer score/upvotes (e.g. between 10 and 300)\n"
        f"- \"comments\": An integer representing the number of comments\n"
        f"- \"url\": A realistic relative or absolute URL (e.g. \"https://reddit.com/r/{subreddit}/comments/...\")"
    )
    fallback = [
        {
            "title": f"Example post about {query}",
            "score": 120,
            "comments": 35,
            "url": f"https://reddit.com/r/{subreddit}/example"
        }
    ]
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