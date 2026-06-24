from duckduckgo_search import DDGS
import json

def test_ddg():
    query = 'site:linkedin.com בניית אתרים OR "אתר לעסק"'
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=5))
        print(f"DDGS LinkedIn Results: {len(results)}")
        for r in results:
            print(r.get('title'))
    except Exception as e:
        print("DDGS Error:", e)

if __name__ == "__main__":
    test_ddg()
