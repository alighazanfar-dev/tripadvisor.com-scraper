import requests
from botasaurus_driver import Driver, Wait
from bs4 import BeautifulSoup
import json
import pandas as pd
import os
from textblob import TextBlob
import logging
import time
import random

# Configuration
TEST_MODE = True  # Set to True to activate Test Mode (scrapes 2 hostels), False to scrape all

# Define the input and output file paths
input_file = 'hostel_links.json'
output_json = 'hostel_data.json'
output_excel = 'hostel_data.xlsx'

# Optionally, modify output filenames for Test Mode
if TEST_MODE:
    output_json = 'hostel_data_test.json'
    output_excel = 'hostel_data_test.xlsx'

# Initialize logging
logging.basicConfig(filename='scraping_errors.log', level=logging.ERROR)

# Initialize the driver
driver = Driver()

def check_for_captcha_iframe():
    script = """
    return !!document.querySelector('iframe[src*="geo.captcha-delivery.com"]');
    """
    return driver.run_js(script)

# Initialize an empty list to store hostel data
hostel_data = []

# Load the hostel links from the JSON file
with open(input_file, 'r') as file:
    hostel_links = json.load(file)

# Activate Test Mode: Limit to first 2 hostels
if TEST_MODE:
    hostel_links = hostel_links[:2]
    print("Test Mode is active: Scraping only the first 2 hostels.")
else:
    print(f"Scraping {len(hostel_links)} hostels.")

# Define the columns for the Excel output
columns = [
    'Row Number', 'Hotel Name', 'Overall Rating', 'Location Rating', 
    'Cleanliness Rating', 'Service Rating', 'Value Rating', 
    'Price per Night', 'Property Amenities', 'Hotel Description', 
    'Review #1', 'Review #2', 'Sentiment #1', 'Sentiment #2', 'Link'
]

# Function to determine sentiment
def analyze_sentiment(text):
    if not text:
        return None
    analysis = TextBlob(text)
    if analysis.sentiment.polarity > 0.1:
        return "Positive"
    elif analysis.sentiment.polarity < -0.1:
        return "Negative"
    else:
        return "Neutral"

# Function to scrape details from a hostel page
def scrape_hostel_data(url, row_num):
    try:
        driver.google_get(url, bypass_cloudflare=True)
        if check_for_captcha_iframe():
            driver.prompt()
        
        time.sleep(4)  # Wait for 4 seconds to let the page load
        driver.scroll_to_bottom()  # Scroll to the bottom of the page
        
        
        page_source = driver.page_html
        soup = BeautifulSoup(page_source, 'html.parser')

        # Extracting the hotel name
        hotel_name = soup.select_one("h1.biGQs").get_text(strip=True) if soup.select_one("h1.biGQs") else None

        # Extracting the ratings
        overall_rating = soup.select_one(".kJyXc.P").get_text(strip=True) if soup.select_one(".kJyXc.P") else None
        location_rating = soup.select_one(".RZjkd:nth-of-type(1) .biKBZ.osNWb").get_text(strip=True) if soup.select_one(".RZjkd:nth-of-type(1) .biKBZ.osNWb") else None
        cleanliness_rating = soup.select_one(".RZjkd:nth-of-type(2) .biKBZ.osNWb").get_text(strip=True) if soup.select_one(".RZjkd:nth-of-type(2) .biKBZ.osNWb") else None
        service_rating = soup.select_one(".RZjkd:nth-of-type(3) .biKBZ.osNWb").get_text(strip=True) if soup.select_one(".RZjkd:nth-of-type(3) .biKBZ.osNWb") else None
        value_rating = soup.select_one(".RZjkd:nth-of-type(4) .biKBZ.osNWb").get_text(strip=True) if soup.select_one(".RZjkd:nth-of-type(4) .biKBZ.osNWb") else None

        # Extracting price per night (if available)
        price_per_night = soup.select_one(".PriceWrapper").get_text(strip=True) if soup.select_one(".PriceWrapper") else None

        # Extracting property amenities
        amenities = [item.get_text(strip=True) for item in soup.select(".Jevoh .gFttI")]
        property_amenities = ', '.join(amenities)

        # Extracting hotel description with updated selector
        hotel_description = soup.select_one("div#GAI_REVIEWS .biGQs._P.pZUbB.KxBGd").get_text(separator=' ', strip=True) if soup.select_one("div#GAI_REVIEWS .biGQs._P.pZUbB.KxBGd") else None

        # Extracting reviews with updated selectors
        reviews = [review.get_text(separator=' ', strip=True) for review in soup.select('span[data-automation^="reviewText_"]')]
        review_1 = reviews[0] if len(reviews) > 0 else None
        review_2 = reviews[1] if len(reviews) > 1 else None

        # Sentiment analysis
        sentiment_1 = analyze_sentiment(review_1)
        sentiment_2 = analyze_sentiment(review_2)

        # Debugging output
        print({
            'Row Number': row_num,
            'Hotel Name': hotel_name,
            'Overall Rating': overall_rating,
            'Location Rating': location_rating,
            'Cleanliness Rating': cleanliness_rating,
            'Service Rating': service_rating,
            'Value Rating': value_rating,
            'Price per Night': price_per_night,
            'Property Amenities': property_amenities,
            'Hotel Description': hotel_description,
            'Review #1': review_1,
            'Review #2': review_2,
            'Sentiment #1': sentiment_1,
            'Sentiment #2': sentiment_2,
            'Link': url
        })

        # Append the scraped data to the list
        hostel_data.append({
            'Row Number': row_num,
            'Hotel Name': hotel_name,
            'Overall Rating': overall_rating,
            'Location Rating': location_rating,
            'Cleanliness Rating': cleanliness_rating,
            'Service Rating': service_rating,
            'Value Rating': value_rating,
            'Price per Night': price_per_night,
            'Property Amenities': property_amenities,
            'Hotel Description': hotel_description,
            'Review #1': review_1,
            'Review #2': review_2,
            'Sentiment #1': sentiment_1,
            'Sentiment #2': sentiment_2,
            'Link': url
        })
        
        # Optional: Implement rate limiting to avoid overloading the server
        time.sleep(random.uniform(2, 5))  # Sleep for 2 to 5 seconds
        
    except Exception as e:
        logging.error(f"Failed to scrape {url}: {e}")
        print(f"Failed to scrape {url}: {e}")

# Loop through each hostel link and scrape data
for idx, link in enumerate(hostel_links):
    print(f"Scraping {idx + 1}/{len(hostel_links)}: {link}")
    scrape_hostel_data(link, idx + 1)

# Save the data to a JSON file
with open(output_json, 'w') as file:
    json.dump(hostel_data, file, indent=4)

# Save the data to an Excel file
df = pd.DataFrame(hostel_data, columns=columns)
df.to_excel(output_excel, index=False)

print(f"Scraping completed. Data saved to {output_json} and {output_excel}.")
