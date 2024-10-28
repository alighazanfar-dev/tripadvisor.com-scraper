import json
from botasaurus_driver import Driver

# Function to generate URLs
def generate_urls(base_url, start_offset, end_offset, increment):
    urls = []
    for offset in range(start_offset, end_offset + increment, increment):
        urls.append(f"{base_url}&offset={offset}")
    return urls

# Base URL with a placeholder for the offset
base_url = "https://www.tripadvisor.com/FindRestaurants?geo=60893&establishmentTypes=10591&broadened=false"

# Generate all the URLs with offsets from 0 to 1350 in increments of 30
urls = generate_urls(base_url, 0, 1350, 30)

# Initialize the driver
driver = Driver()

# Base URL for attaching to the extracted links
base_url_prefix = "https://www.tripadvisor.com"

# Array to store all product links
productlinks = []

# Visit each URL and extract links
for url in urls:
    driver.google_get(url, bypass_cloudflare=True)
    links = driver.get_all_links('.biGQs a.BMQDV')
    # Attach base URL to each extracted link and add to the productlinks array
    full_links = [base_url_prefix + link for link in links]
    productlinks.extend(full_links)

# Save the product links to a JSON file
with open('productlinks.json', 'w') as file:
    json.dump(productlinks, file, indent=4)

# Print a message indicating completion
print("Product links have been saved to productlinks.json")
