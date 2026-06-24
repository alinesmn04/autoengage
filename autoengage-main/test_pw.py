from playwright.sync_api import sync_playwright

def test_pw_search():
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto('https://lite.duckduckgo.com/lite/')
            page.fill('input[name="q"]', 'site:linkedin.com/posts "אני רוצה אתר"')
            page.click('button[type="submit"]')
            page.wait_for_selector('.result-snippet', timeout=5000)
            elements = page.query_selector_all('.result-snippet')
            print("Found snippets:", len(elements))
            for el in elements:
                print(el.inner_text())
            browser.close()
    except Exception as e:
        print("Playwright error:", e)

if __name__ == "__main__":
    test_pw_search()
