import requests
import json

API_KEY = "e971cece7fmsh029effc64849cf3p10be7cjsnc23c8322039c"

def test_linkedin():
    host = "realtime-linkdin-scraper1.p.rapidapi.com"
    ep = "/search.php"
    url = f"https://{host}{ep}"
    headers = {"x-rapidapi-key": API_KEY, "x-rapidapi-host": host}
    params = {"searchTerm": "automation"}
    r = requests.get(url, headers=headers, params=params)
    print(f"LinkedIn {ep} -> {r.status_code}")
    print("Response:", r.text[:200])

if __name__ == "__main__":
    test_linkedin()
