import json
import time
from pathlib import Path
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

CATALOG_URL = "https://www.shl.com/products/product-catalog/"

def extract_products(html):
    soup = BeautifulSoup(html, "html.parser")
    rows = soup.select("tr[data-entity-id]")

    products = []
    for row in rows:
        cols = row.find_all("td")
        if len(cols) < 4:
            continue

        a_tag = row.select_one("td.custom__table-heading__title a")
        if not a_tag:
            continue

        name = a_tag.get_text(strip=True)
        href = a_tag.get("href")
        url = href if href.startswith("http") else f"https://www.shl.com{href}"

        remote = "Yes" if "●" in cols[1].get_text(strip=True) else "No"
        adaptive = "Yes" if "●" in cols[2].get_text(strip=True) else "No"
        test_type = cols[3].get_text(strip=True)

        products.append({
            "name": name,
            "url": url,
            "remote_support": remote,
            "adaptive_support": adaptive,
            "test_type": test_type
        })

    return products


def scrape_catalog():
    all_products = []
    base_url = "https://www.shl.com/products/product-catalog/?start={}&type=1"

    with sync_playwright() as p:
        print("Launching browser ...")
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        for page_num in range(0, 32):  # 32 pages
            url = base_url.format(page_num * 12)
            print(f"Scraping page {page_num+1} — {url}")
            page.goto(url, wait_until="networkidle")
            time.sleep(2)

            html = page.content()
            page_products = extract_products(html)
            all_products.extend(page_products)
            print(f"Total items so far: {len(all_products)}")

        browser.close()

    # save output
    out_path = Path(__file__).resolve().parent.parent / "backend" / "data" / "catalog_raw.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)

    with out_path.open("w", encoding="utf-8") as f:
        json.dump(all_products, f, indent=2, ensure_ascii=False)

    print("\n🎉 FINAL TOTAL:", len(all_products), "products scraped")

if __name__ == "__main__":
    scrape_catalog()
