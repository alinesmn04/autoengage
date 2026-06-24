import requests

url = "https://google-search74.p.rapidapi.com/"
headers = {
    "x-rapidapi-key": "e971cece7fmsh029effc64849cf3p10be7cjsnc23c8322039c",
    "x-rapidapi-host": "google-search74.p.rapidapi.com"
}

params = {
    "query": "site:linkedin.com/posts/ marketing",
    "limit": "10",
    "related_keywords": "true"
}

try:
    response = requests.get(url, headers=headers, params=params)
    print("Status:", response.status_code)
    print("Response:", response.text[:1000])
except Exception as e:
    print("Error:", e)
