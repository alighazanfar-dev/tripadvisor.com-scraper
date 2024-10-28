from botasaurus_driver import Driver, Wait
from bs4 import BeautifulSoup
import json

# Initialize the driver
driver = Driver()

# Fetch the page content
url = "https://www.tripadvisor.com/Restaurant_Review-g60893-d23528567-Reviews-Fall_Line_Kitchen_Bar-Richmond_Virginia.html"
driver.google_get(url, bypass_cloudflare=True)
page_source = driver.page_html
soup = BeautifulSoup(page_source, 'html.parser')
#driver.scroll()


# Extract the restaurant name

try:
    Restaurantname = soup.find('h1', class_='biGQs _P egaXP rRtyp').text.strip()
except AttributeError:
    Restaurantname = "Name Not Found"

try:
    Rating = soup.find('span', class_='uuBRH').text.strip()
except AttributeError:
    Rating = ""

try:
    ReviewsCount = soup.find('span', class_='oXJmt').text.strip()
except AttributeError:
    ReviewsCount = ""


address_element = soup.select_one('div.hpxwy.e.j a[href^="https://maps.google.com"] span')
Address = address_element.text.strip() if address_element else ""


website_element = soup.select_one('a[aria-label="Website"]')
Website = website_element['href'] if website_element else ""


email_element = soup.select_one('a[aria-label="Email"]')
Email = email_element['href'].replace('mailto:', '') if email_element else ""


phone_element = soup.select_one('a[aria-label="Call"] span')
Phone = phone_element.text if phone_element else ""


about_element = soup.select_one('.AYNtL div.pZUbB')
About = about_element.text.strip() if about_element else ""

cuisine_element = soup.select_one('div.SFSXn:nth-of-type(1) div:nth-of-type(1) div.pZUbB')
Cuisine = cuisine_element.text.strip() if cuisine_element else ""

special_diet_element = soup.select_one('div.SFSXn:nth-of-type(1) div:nth-of-type(2) div.pZUbB')
SpecialDiet = special_diet_element.text.strip() if special_diet_element else ""

meals_element = soup.select_one('div.SFSXn:nth-of-type(2) div:nth-of-type(1) div.pZUbB')
Meals = meals_element.text.strip() if meals_element else ""

features_element = soup.select_one('div.SFSXn:nth-of-type(2) div:nth-of-type(2) div.pZUbB')
Features = features_element.text.strip() if features_element else ""

price_range_element = soup.select_one('span:nth-of-type(1) .biGQs span.hmDzD')
PriceRange = price_range_element.text.strip() if price_range_element else ""

category_element = soup.select_one('.fSuCF button.BmgDU')
Category = category_element.text.strip() if category_element else ""


open_hours_elements = soup.find_all('span', class_='biGQs _P pZUbB egaXP hmDzD')

# Iterate over each element to extract the text
open_hoursss = [element.text.strip() for element in open_hours_elements]


day_elements = soup.find_all('div', class_='VFyGJ Pi')

# Initialize an empty dictionary to store opening hours for each day
opening_hours = {}

# Iterate over each day element to extract day names and opening hours
for day in day_elements:
    # Find the day of the week
    day_name = day.find('div', class_='biGQs _P pZUbB hmDzD').text.strip()
    
    # Find the opening hours for that day
    hours_spans = day.find_all('span', class_='biGQs _P pZUbB egaXP hmDzD')
    
    # Extract the opening hours as a list of strings
    hours = [span.text.strip() for span in hours_spans]
    
    # Store the opening hours for the day
    opening_hours[day_name] = hours


hours_element = soup.find('div', class_='DgJpu')

rating_spans = soup.find_all('span', class_='biGQs')

ratings = {}

for span in rating_spans:
    category = span.text.strip()  # Extract the category
    if category in ['Food', 'Service', 'Value', 'Atmosphere']:
        svg_div = span.find_next_sibling('div')
        aria_labelledby = svg_div.find('svg')['aria-labelledby']
        title_element = soup.find('title', id=aria_labelledby)
        rating = title_element.text.strip()
        ratings[category] = rating



restaurant_data = {
    "RestaurantName": Restaurantname,
    "Rating": Rating,
    "Food Rating": ratings.get("Food", " "),
    "Service Rating": ratings.get("Service", " "),
    "Value Rating": ratings.get("Value", " "),
    "Atmosphere Rating": ratings.get("Atmosphere", " "),
    "No of Reviews": ReviewsCount,
    "Address": Address,
    "Email": Email,
    "Phone": Phone,
    "Website": Website,
    "About": About,
    "Cuisine": Cuisine,
    "Special Diet": SpecialDiet,
    "Meals": Meals,
    "Features": Features,
    "Price Range": PriceRange,
    "Category": Category,
    "Open Hours": opening_hours
}
print(restaurant_data)


print("Data has been saved to restaurant_data.json")
