import requests
import time
import json

def test_campaign():
    print("Creating campaign...")
    res = requests.post("http://127.0.0.1:8000/api/campaigns", json={
        "name": "Custom LinkedIn Campaign - Website Building",
        "platform": "LinkedIn",
        "query": "posts/ בניית אתרים",
        "subreddit": ""
    })
    
    if res.status_code != 200:
        print("Failed to create campaign:", res.text)
        return
        
    data = res.json()
    camp_id = data["campaign"]["id"]
    print(f"Created campaign {camp_id}")
    
    print("Triggering campaign...")
    res2 = requests.post(f"http://127.0.0.1:8000/api/campaigns/{camp_id}/trigger")
    if res2.status_code != 200:
        print("Failed to trigger:", res2.text)
        return
        
    print("Trigger result:")
    print(json.dumps(res2.json(), indent=2))
    
    print("\nLogs from campaign:")
    for log in res2.json()["campaign"]["logs"]:
        print(log)

if __name__ == "__main__":
    test_campaign()
