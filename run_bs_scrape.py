import requests
from bs4 import BeautifulSoup
from datetime import datetime

# Config
URL = "https://www.silverdoor.com/serviced-apartments/united-kingdom/london/?bed_type=3BedroomApartment&postcode=CR0+1NN&withResults=1"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
}
COUNTRY = "GB"
CITY = "London"
CURRENCY = "GBP"
PROVIDER = "Silverdoor"
SCREENSHOT = "Screenshot_2025-06-21_at_20.56.17.png"  # Replace with your screenshot filename

def main():
    # Step 1: Get the HTML
    resp = requests.get(URL, headers=HEADERS)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, 'html.parser')

    # Step 2: Extract property results
    results = []
    for prop in soup.select('.js-property-result-data'):
        # Apartment type: Find previous card and parse "1 Bed", "2 Bed", "3 Bed"
        types = []
        card = prop.find_previous('div', class_='sda-property-card')
        if card:
            types_text = card.get_text()
            if '1 Bed' in types_text:
                types.append('1 bedroom')
            if '2 Bed' in types_text:
                types.append('2 bedrooms')
            if '3 Bed' in types_text:
                types.append('3 bedrooms')
        apartment_type = ', '.join(types) if types else None

        # Address: use data-location
        address = prop.get('data-location', None)

        # Price & currency
        price = prop.get('data-rate', None)
        currency = CURRENCY  # Default
        if price and price.strip().startswith("£"):
            currency = "GBP"

        # Minimum stay (not available in search listing—set as None)
        minimum_stay = None

        # Datetime of scraping
        scraped_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # Build result
        result = {
            "country": COUNTRY,
            "city": CITY,
            "apartment_type": apartment_type,
            "address": address,
            "price": price,
            "currency": currency,
            "scraped_at": scraped_at,
            "minimum_stay": minimum_stay,
            "screenshot": SCREENSHOT,
            "provider": PROVIDER,
            "title": prop.get('data-name', None),
            "listing_url": "https://www.silverdoor.com" + prop.get('data-href', ''),
            "image_url": prop.get('data-img-src', None)
        }
        results.append(result)

    # Step 3: Print (or save) the results
    from pprint import pprint
    pprint(results)
    print(f"Extracted {len(results)} listings.")

if __name__ == '__main__':
    main()
