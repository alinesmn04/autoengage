import requests

API_KEY = "e971cece7fmsh029effc64849cf3p10be7cjsnc23c8322039c"
url = "https://reddit34.p.rapidapi.com/getSearchPosts"
headers = {
    "x-rapidapi-key": API_KEY,
    "x-rapidapi-host": "reddit34.p.rapidapi.com"
}

r1 = requests.get(url, headers=headers, params={"q": "test"})
print("Only q:", r1.text[:100])

r2 = requests.get(url, headers=headers, params={"query": "test"})
print("Only query:", r2.text[:100])

r3 = requests.get(url, headers=headers, params={"searchTerm": "test"})
print("Only searchTerm:", r3.text[:100])
