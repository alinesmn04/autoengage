from duckduckgo_search import DDGS
import json

def test_ddg():
    try:
        query = 'site:linkedin.com/posts "מחפש בונה אתרים"'
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=3))
        print("Results:", len(results))
        for r in results:
            print(r['title'])
    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    test_ddg()
