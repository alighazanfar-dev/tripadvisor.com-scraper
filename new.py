from botasaurus_driver import Driver, Wait
import json
import time

# Initialize the driver
driver = Driver()

# Fetch the page content
url = "https://www.tripadvisor.com/Hotels-g187147-a_travelersChoice.1-Paris_Ile_de_France-Hotels.html"
driver.google_get(url, bypass_cloudflare=True)


def check_for_captcha_iframe():
    script = """
    return !!document.querySelector('iframe[src*="geo.captcha-delivery.com"]');
    """
    return driver.run_js(script)


if check_for_captcha_iframe():
    driver.prompt()

def check_for_pagination():
    """
    Check if pagination exists on the page.
    """
    pagination_selector = 'div[data-automation="Paginator"]'
    return driver.is_element_present(pagination_selector)

def extract_hostel_links():
    """
    Extract hostel links from the JSON-LD script on the page.
    """
    script_selector = 'div[data-test-target="hotels-json-ld"] > script[type="application/ld+json"]'
    json_ld_script = driver.get_text(script_selector)
    if not json_ld_script:
        return []

    # Parse the JSON-LD data
    data = json.loads(json_ld_script)
    if "itemListElement" not in data:
        return []

    # Extract URLs for each hostel
    hostel_links = [item['item']['url'] for item in data['itemListElement']]
    return hostel_links

def go_to_next_page():
    """
    Click the "Next page" arrow to go to the next page of results.
    """
    next_button_selector = 'a[data-smoke-attr="pagination-next-arrow"]'
    driver.click(next_button_selector)
    time.sleep(4)  # Wait for 4 seconds to let the page load
    driver.scroll_to_bottom()  # Scroll to the bottom of the page

# List to hold all the hostel links
all_hostel_links = []

# Loop through the pages while pagination exists
while True:
    # Extract hostel links from the current page
    links = extract_hostel_links()
    print(f"Found {len(links)} hostel links")
    all_hostel_links.extend(links)

    # Check if a next page exists
    if not check_for_pagination():
        break

    # Go to the next page
    try:
        go_to_next_page()
    except Exception as e:
        print("Reached the last page or an error occurred:", e)
        break

# Save all the hostel links to a JSON file
with open('hostel_links.json', 'w') as file:
    json.dump(all_hostel_links, file, indent=4)

print(f"Extracted {len(all_hostel_links)} hostel links.")
print("Data has been saved to hostel_links.json")