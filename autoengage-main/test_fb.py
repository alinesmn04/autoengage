import requests
import json

API_KEY = "e971cece7fmsh029effc64849cf3p10be7cjsnc23c8322039c"

def test_fb():
    host = "facebook-scraper3.p.rapidapi.com"
    endpoints = ["/search/posts", "/search", "/search/top", "/posts/search", "/api/search"]
    for ep in endpoints:
        url = f"https://{host}{ep}"
        headers = {"x-rapidapi-key": API_KEY, "x-rapidapi-host": host}
        params = {"query": "automation", "q": "automation", "keyword": "automation"}
        try:
            r = requests.get(url, headers=headers, params=params)
            print(f"Facebook {ep} -> {r.status_code}")
            if r.status_code == 200:
                print("Response:", r.text[:200])
        except Exception as e:
            print("Error:", e)

if __name__ == "__main__":
    test_fb()
