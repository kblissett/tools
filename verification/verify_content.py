from playwright.sync_api import sync_playwright

def verify_kanji_content():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # Navigate
        page.goto("http://localhost:8080/kanji_dashboard.html")

        # Search
        page.fill("#kanji-input", "会議室")
        page.click("#search-btn")

        # Wait for results
        try:
            page.wait_for_selector(".kanji-card", timeout=10000)
            page.wait_for_timeout(5000)

            # Extract content from the first card
            card1 = page.locator("#card-会")
            if card1.count() > 0:
                char = card1.locator(".kanji-char").inner_text()
                meaning = card1.locator(".kanji-meaning").inner_text()
                readings = card1.locator(".kanji-readings").inner_text()

                print(f"Card 1 Char: {char}")
                print(f"Card 1 Meaning: {meaning}")
                print(f"Card 1 Readings: {readings}")

                # Check anchors
                anchors = card1.locator(".anchor-word").all_inner_texts()
                print(f"Card 1 Anchors: {anchors[:3]}")

            else:
                print("Card for '会' not found by ID. Fetching first card.")
                first_card = page.locator(".kanji-card").first
                print(f"First Card Text: {first_card.inner_text()[:100]}")

        except Exception as e:
            print(f"Error: {e}")

        browser.close()

if __name__ == "__main__":
    verify_kanji_content()
