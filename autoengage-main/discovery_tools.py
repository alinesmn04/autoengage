"""
Discovery tools for AutoEngage.

This module helps the agent find viral posts, read web pages,
and score how relevant a post is to the brand niche.
"""

import requests
from bs4 import BeautifulSoup
from langchain_core.tools import tool


@tool
def search_viral_posts(query: str, max_results: int = 5) -> str:
    """
    Search for viral or relevant posts based on a query.
    Returns a simple list of search result titles and links.
    """

    search_url = f"https://www.google.com/search?q={query}"
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    try:
        response = requests.get(search_url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")

        results = []
        links = soup.find_all("a")

        for link in links:
            href = link.get("href")
            text = link.get_text().strip()

            if href and text and href.startswith("/url?q="):
                clean_link = href.split("/url?q=")[1].split("&")[0]
                results.append(f"{len(results) + 1}. {text} - {clean_link}")

            if len(results) >= max_results:
                break

        if not results:
            return "No results found."

        return f"Found {len(results)} results:\n" + "\n".join(results)

    except Exception as e:
        return f"Error while searching: {str(e)}"


@tool
def read_post_content(url: str) -> str:
    """
    Read a web page and return clean text content up to 2000 characters.
    """

    if not url.startswith("http"):
        return "Error: URL must start with http or https."

    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")

        text = soup.get_text(separator=" ", strip=True)
        return text[:2000]

    except Exception as e:
        return f"Error while reading page: {str(e)}"


@tool
def score_relevance(post_text: str, niche: str) -> str:
    """
    Score how relevant a post is to the business niche.
    Returns a score from 0 to 100 with an explanation.
    """

    post_lower = post_text.lower()
    niche_words = niche.lower().split()

    matches = 0

    for word in niche_words:
        if word in post_lower:
            matches += 1

    score = int((matches / len(niche_words)) * 100) if niche_words else 0

    if score >= 70:
        explanation = "The post is highly relevant to the niche."
    elif score >= 40:
        explanation = "The post is somewhat relevant to the niche."
    else:
        explanation = "The post is not very relevant to the niche."

    return f"Score: {score}/100\nExplanation: {explanation}"