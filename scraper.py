
from datetime import datetime
from playwright.sync_api import sync_playwright
import pandas as pd

def get_valid_date(prompt):
    while True:
        user_input = input(prompt)
        try:
            date_obj = datetime.strptime(user_input, '%d-%m-%Y')
            return date_obj.strftime('%Y-%m-%d')
        except ValueError:
            print("Invalid format. Please enter the date as DD-MM-YYYY (e.g. 23-06-2025).")

def main():
    city = input("Enter city (e.g. Tokyo, Osaka, Kyoto): ").strip()
    checkin = get_valid_date("Enter check-in date (DD-MM-YYYY): ")
    checkout = get_valid_date("Enter check-out date (DD-MM-YYYY): ")

    url = (
        f'https://www.booking.com/searchresults.en-gb.html?'
        f'ss={city}&ssne={city}&ssne_untouched={city}'
        f'&checkin={checkin}&checkout={checkout}'
        f'&group_adults=2&group_children=0&no_rooms=1'
        f'&dest_type=city&selected_currency=USD'
    )

    print(f"\nCity: {city}")
    print(f"Check-in: {checkin}")
    print(f"Check-out: {checkout}")
    print(f"Booking URL:\n{url}\n")

    hotels_list = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        page.goto(url, timeout=60000)

        hotels = page.locator('[data-testid="property-card"]').all()
        print(f"Found {len(hotels)} hotels.")

        for hotel in hotels:
            hotel_dict = {}

            try:
                hotel_dict['name'] = hotel.locator('[data-testid="title"]').inner_text()
            except:
                hotel_dict['name'] = 'N/A'

            try:
                hotel_dict['price'] = hotel.locator('[data-testid="price-and-discounted-price"]').inner_text()
            except:
                hotel_dict['price'] = 'N/A'

            try:
                hotel_dict['score'] = hotel.locator('[data-testid="review-score"] >> div >> nth=0').inner_text()
            except:
                hotel_dict['score'] = 'N/A'

            try:
                hotel_dict['reviews'] = hotel.locator('[data-testid="review-score"] >> div >> nth=2').inner_text()
            except:
                hotel_dict['reviews'] = 'N/A'

            try:
                hotel_dict['distance'] = hotel.locator('[data-testid="distance"]').inner_text()
            except:
                hotel_dict['distance'] = 'N/A'

            hotels_list.append(hotel_dict)

        browser.close()

    df = pd.DataFrame(hotels_list)

    # Clean and convert price and score for sorting
    df['price_clean'] = (
        df['price']
        .str.replace(r'[^\d.]', '', regex=True)
        .replace('', '0')
        .astype(float)
    )

    df['score_clean'] = pd.to_numeric(df['score'], errors='coerce').fillna(0)

    # Ask user how to sort
    sort_by = input("Sort by 'price' or 'score'? ").strip().lower()
    if sort_by == 'score':
        df_sorted = df.sort_values(by='score_clean', ascending=False)
    else:
        df_sorted = df.sort_values(by='price_clean')

    # Save result
    filename = f'hotels_{city.lower()}_sorted.csv'
    df_sorted.to_csv(filename, index=False)
    print(f"Sorted data saved to {filename}")

if __name__ == '__main__':
    main()



