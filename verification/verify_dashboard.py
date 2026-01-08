from playwright.sync_api import sync_playwright

def verify_kanji_dashboard():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # Navigate to the dashboard
        page.goto("http://localhost:8080/kanji_dashboard.html")

        # Wait for the page to load
        page.wait_for_selector("#kanji-input")

        # Type a compound word
        page.fill("#kanji-input", "会議室")
        page.click("#search-btn")

        # Wait for results to appear (check for at least one card)
        try:
            # Wait for at least one kanji card to be present
            page.wait_for_selector(".kanji-card", timeout=10000)

            # Wait a bit more for data to populate (fetch can be slow)
            # We can wait for a specific element that appears after fetch, like .reading-on
            # But since it's async, let's just wait a reasonable amount or wait for loading skeletons to disappear
            # Wait for text content to not be empty in meaning
            page.wait_for_timeout(5000)

            # Take a screenshot
            page.screenshot(path="verification/dashboard_result.png", full_page=True)
            print("Screenshot taken successfully.")

        except Exception as e:
            print(f"Error waiting for results: {e}")
            page.screenshot(path="verification/dashboard_error.png")

        browser.close()

if __name__ == "__main__":
    verify_kanji_dashboard()
