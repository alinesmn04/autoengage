import httpx
import json

try:
    print("Sending request to server...")
    r = httpx.post(
        'http://127.0.0.1:8000/api/chat', 
        json={'message': 'שלום, מה אתה יכול לעשות?'}, 
        timeout=30.0
    )
    print("Status Code:", r.status_code)
    print("Response JSON:")
    print(json.dumps(r.json(), indent=2, ensure_ascii=True))
except Exception as e:
    print("Error:", e)
