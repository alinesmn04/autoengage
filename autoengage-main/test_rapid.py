import requests
url = "https://realtime-linkdin-data-scraper.p.rapidapi.com/search-posts"
querystring = {"query": "automation"}
headers = {
    "x-rapidapi-key": "e971cece7fmsh029effc64849cf3p10be7cjsnc23c8322039c",
    "x-rapidapi-host": "realtime-linkdin-data-scraper.p.rapidapi.com"
}
try:
    response = requests.get(url, headers=headers, params=querystring)
    print("Status:", response.status_code)
    print("Response:", response.text[:1000])
except Exception as e:
    print("Exception:", e)
