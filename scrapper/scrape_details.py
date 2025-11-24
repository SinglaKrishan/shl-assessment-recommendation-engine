import json
import time
from pathlib import Path
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup


INPUT_FILE = Path(__file__).resolve().parent.parent / "backend" / "data" / "catalog_raw.json"
OUTPUT_FILE = Path(__file__).resolve().parent.parent / "backend" / "data" / "catalog_full.json"


def extract_details(html):
    soup = BeautifulSoup(html, "html.parser")

    # Title
    title = soup.select_one("h1")
    title = title.get_text(strip=True) if title else ""

    # Description
    desc_header = soup.find("h4", string="Description")
    description = ""
    if desc_header:
        desc_p = desc_header.find_next("p")
        if desc_p:
            description = desc_p.get_text(strip=True)

    # Job levels
    job_header = soup.find("h4", string="Job levels")
    job_levels = ""
    if job_header:
        job_p = job_header.find_next("p")
        if job_p:
            job_levels = job_p.get_text(strip=True)

    return {
        "long_description": description,
        "job_levels": job_levels
    }


def scrape_details():
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        products = json.load(f)

    updated = []

    # If previous run partially completed → resume
    if OUTPUT_FILE.exists():
        with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
            saved = json.load(f)
            updated.extend(saved)

    start_index = len(updated)
    print(f"Resuming from index: {start_index}")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        page.set_default_timeout(60000)  # 60 seconds timeout

        for i in range(start_index, len(products)):
            product = products[i]
            print(f"[{i+1}/{len(products)}] Scraping: {product['name']}")

            success = False
            retries = 3
            while retries > 0 and not success:
                try:
                    page.goto(product["url"], wait_until="domcontentloaded")
                    time.sleep(1.5)
                    html = page.content()
                    extra = extract_details(html)
                    updated.append({**product, **extra})
                    success = True
                except Exception as e:
                    print("Retry due to error:", e)
                    retries -= 1
                    time.sleep(3)

            # Save progress after each product
            with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
                json.dump(updated, f, indent=2, ensure_ascii=False)

        browser.close()

    print("\n🎉 Detailed scraping complete!")
    print(f"🎯 Total saved: {len(updated)}")
    print("📦 File:", OUTPUT_FILE)


if __name__ == "__main__":
    scrape_details()
