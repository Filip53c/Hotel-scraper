from playwright.sync_api import sync_playwright
import pandas as pd
from datetime import datetime

def get_valid_date(prompt):
    while True:
        user_input = input(prompt).strip()
        try:
            datetime.strptime(user_input, '%d-%m-%Y')
            return user_input
        except ValueError:
            print("Invalid format. Please use dd-MM-YYYY.")

def main():
    city = input("Enter city (e.g. Paris, Tokyo, Belgrade): ").strip()
    checkin_date = get_valid_date("Enter check-in date (DD-MM-YYYY): ")
    checkout_date = get_valid_date("Enter check-out date (DD-MM-YYYY): ")

    page_url = (
        f'https://www.booking.com/searchresults.en-us.html'
        f'?checkin={checkin_date}&checkout={checkout_date}'
        f'&selected_currency=EUR&ss={city}&ssne={city}&ssne_untouched={city}'
        f'&lang=en-us&sb=1&src_elem=sb&src=searchresults'
        f'&dest_type=city&group_adults=1&no_rooms=1&group_children=0&sb_travel_purpose=leisure'
    )

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        page.goto(page_url, timeout=60000)

        hotels = page.locator('[data-testid="property-card"]').all()
        print(f'There are: {len(hotels)} hotels.')

        hotels_list = []
        for hotel in hotels:
            hotel_dict = {}

            title = hotel.locator('[data-testid="title"]')
            price = hotel.locator('[data-testid="price-and-discounted-price"], [data-testid="price"]')
            score = hotel.locator('[data-testid="review-score"] >> div').nth(0)
            review_text = hotel.locator('[data-testid="review-score"] >> div').nth(2)
            distance = hotel.locator('[data-testid="distance"]')

            if title.count() > 0:
                title_text = title.inner_text().strip()
                hotel_dict['hotel'] = " ".join(title_text.splitlines())
            else:
                hotel_dict['hotel'] = 'N/A'

            hotel_dict['price'] = price.inner_text().strip() if price.count() > 0 else 'N/A'
            hotel_dict['score'] = score.inner_text().strip() if score.count() > 0 else 'N/A'
            hotel_dict['reviews count'] = review_text.inner_text().strip() if review_text.count() > 0 else 'N/A'
            hotel_dict['distance'] = distance.inner_text().strip().replace("downtown", "center").replace("Downtown", "center") if distance.count() > 0 else 'N/A'

            hotels_list.append(hotel_dict)

        df = pd.DataFrame(hotels_list)
        df.to_excel('hotels_list.xlsx', index=False)
        df.to_csv('hotels_list.csv', index=False)

        browser.close()


if __name__ == '__main__':
    main()
