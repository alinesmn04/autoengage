import requests

API_KEY = "e971cece7fmsh029effc64849cf3p10be7cjsnc23c8322039c"

def test_linkedin():
    host = "realtime-linkdin-scraper1.p.rapidapi.com"
    # Let's try guessing the endpoint or use the user's example to ensure subscription works
    print("Testing LinkedIn Subscription...")
    url = f"https://{host}/companySearch.php"
    headers = {"x-rapidapi-key": API_KEY, "x-rapidapi-host": host}
    try:
        r = requests.get(url, headers=headers, params={"searchTerm": "stripe"})
        print(f"Company Search Status: {r.status_code}")
    except Exception as e:
        print("Error:", e)

def test_reddit():
    host = "reddit34.p.rapidapi.com"
    print("\nTesting Reddit Subscription...")
    url = f"https://{host}/getPostCommentsWithSortV2"
    headers = {"x-rapidapi-key": API_KEY, "x-rapidapi-host": host}
    try:
        r = requests.get(url, headers=headers, params={"post_url": "https://www.reddit.com/r/AskReddit/comments/ablzuq/people_who_have_been_to_prison_what_is_it_really/", "sort": "new"})
        print(f"Comment Fetch Status: {r.status_code}")
    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    test_linkedin()
    test_reddit()
