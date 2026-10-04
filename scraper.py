from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

def fetch_product_price(url: str) -> float:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        )
        page = context.new_page()
        page.goto(url, wait_until="domcontentloaded")
        page.wait_for_selector(".ads-pb__price-value")
        html_content = page.content()
        browser.close()
    
    soup = BeautifulSoup(html_content, "html.parser")
    price_element = soup.find("span", class_="ads-pb__price-value js-price-box__primary-price__value")
    
    if not price_element:
        raise ValueError("Price element not found on page")

    raw_text = price_element.text
    clean_text = raw_text.replace(",", ".").replace("\xa0", "").replace(" ", "")
    price_number = "".join(char for char in clean_text if char.isdigit() or char == ".")
    
    return float(price_number)




# if __name__ == "__main__":
#     test_url = "https://www.alza.cz/omen-by-hp-35l-gt16-0912nc-d13425511.htm"
#     price = fetch_product_price(test_url)
#     print(f"Scraped Price: {price} (Type: {type(price)})")

    

