import requests

url = "https://webapi.alza.cz/api/commodity/v1/12553669?country=CZ&pgrik=p_pg2_a25f3&ucik=u_cr3lg1_baf47&isInStock=True"

# Spoof browser headers to bypass basic API blocks
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Referer": "https://www.alza.cz/",
    "Accept": "application/json, text/plain, */*"
}

response = requests.get(url, headers=headers)

print("Status Code:", response.status_code)

if response.status_code == 200:
    data = response.json()
    price = data["priceInfo"]["priceNoCurrency"]
    print(f"Scraped Price: {float(price)} CZK")
else:
    print("Failed to fetch JSON. Server response:")
    print(response.text[:300])  # Print first 300 characters of the error response