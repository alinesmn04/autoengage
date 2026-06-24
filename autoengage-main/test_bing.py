import requests
from bs4 import BeautifulSoup
import json

def test_bing():
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    query = 'site:linkedin.com/posts "בניית אתרים"' # Broader query for testing
    url = f"https://www.bing.com/search?q={query}"
    res = requests.get(url, headers=headers)
    soup = BeautifulSoup(res.text, 'html.parser')
    results = []
    for a in soup.select("ol#b_results h2 a"):
        results.append({"title": a.text, "url": a.get("href")})
    
    with open("bing_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print("Done. Found:", len(results))

if __name__ == "__main__":
    test_bing()
