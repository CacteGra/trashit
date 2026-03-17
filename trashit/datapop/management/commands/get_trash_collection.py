from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, ElementClickInterceptedException

import time

from datapop.models import RegisterAPI
from trash.models import CollectArea

from collections import Counter

def get_dicts_with_same_value(dict_list, key):
    """Get dictionaries that have the same value for a specific key"""
    # Count occurrences of each value
    value_counts = Counter(d[key] for d in dict_list if key in d)
    
    # Get values that appear more than once
    duplicate_values = {value for value, count in value_counts.items() if count > 1}
    
    # Return dictionaries with duplicate values
    return [d for d in dict_list if key in d and d[key] in duplicate_values]

def drive_url(url):
    # Configure Selenium options
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")
    print('TO DRIVER')
    driver = webdriver.Remote(
            command_executor='http://hub:4444/wd/hub',
        options=chrome_options
    )
    print(driver)
    driver.get(url)
    print('GOT')
    wait = WebDriverWait(driver, 10)
    pins = wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, "mapplic-pin")))
    time.sleep(5)  # Wait for the page to load
    return driver, pins, wait

def get_info_from_pin(driver, wait, pin, i, location, waste_data):
    # Scroll the element into view first
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", pin)
    time.sleep(1)
    
    # Click the pin to show tooltip
    pin.click()
    
    # Wait for tooltip to appear
    tooltip = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "mapplic-tooltip")))
    
    # Extract the tooltip text
    tooltip_text = tooltip.text
    
    # Store the data
    if tooltip_text:
        waste_data.append({
            "pin_index": i,
            "location": location,
            "tooltip_content": tooltip_text
        })
    
    # Close the tooltip before clicking another pin
    try:
        close_button = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "mapplic-tooltip-close")))
        close_button.click()
        time.sleep(2)
    except TimeoutException:
        print(f"Pin {i} ({location}): No close button found, continuing...")
    
    print(f"Pin {i} ({location}): Successfully extracted and closed data")


def main(data_lines):

    # URL of the waste collection page
    url = "https://intersites.agglo-larochelle.fr/plan-dechets-2026/"

    try:
        # Fetch the page
        driver, pins, wait = drive_url(url)
        
        # Store the collected data
        waste_data = []
        
        done_locations = []
        
        # Iterate through each pin
        for i, pin in enumerate(pins):
            try:
                # Get the data-location attribute
                print("BEFORE LOC")
                current_pins = wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, "mapplic-pin")))
                pin = current_pins[i]  # Get the same pin from current list
                location = pin.get_attribute("data-location")
                print(location)
                if location in done_locations:
                    continue
                done_locations.append(location)
                # Skip the pin with data-location="la-rochelle"
                if location == "la-rochelle":
                    continue
                elif location == "chatelaillon-plage":
                    pin.click()
                    time.sleep(5)
                    chatel_pins = wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, "map-area")))
                    chatel_data = []
                    for chatel_pin in chatel_pins:
                        get_info_from_pin(driver, wait, chatel_pin, i, location, waste_data)
                    waste_data.append(chatel_data)
                    print(waste_data)
                    back_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".btn.btn--secondary.item-back")))
                    back_button.click()
                    time.sleep(5)
                    # Reload pins with page change
                    #driver, pins, wait = drive_url(url)
                    print("AFTER DRIVER")
                else:
                    get_info_from_pin(driver, wait, pin, i, location, waste_data)
                
            except (ElementClickInterceptedException, TimeoutException) as e:
                print(f"Error processing pin {i} ({location}): {e}")
                continue
        
        # Close Selenium driver
        driver.quit()
        
        # Print results
        for data in waste_data:
            c_a = CollectArea.objects.get(description__icontains=data['location'])
            same_locations = get_dicts_with_same_value(waste_data, 'location')
            if same_locations.count > 1:
                same_location_description = ''
                for same_location in same_locations:
                    same_location_description += data['tooltip_content']
                c_a.description = same_location_description
            else:
                c_a.description = data['tooltip_content']
            c_a.save()
            print(f"Location: {data['location']}")
            print(f"Data: {data['tooltip_content']}")
            print("---")
        
        print(f"Total pins processed (excluding La Rochelle): {len(waste_data)}")
        
    except Exception as e:
        driver.quit()
