from googlesearch import search

def test_google():
    query = 'python'
    results = []
    try:
        for j in search(query, num_results=2, advanced=True):
            results.append({"title": j.title, "url": j.url, "description": j.description})
    except Exception as e:
        print("Error:", e)
    
    print("Found:", len(results))
    for r in results:
        print(r['title'])

if __name__ == "__main__":
    test_google()
