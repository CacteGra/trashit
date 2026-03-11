from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, ElementClickInterceptedException
import time

# Configure Selenium options
chrome_options = Options()
chrome_options.add_argument("--headless")
driver = webdriver.Chrome(options=chrome_options)

# URL of the waste collection page
url = "https://intersites.agglo-larochelle.fr/plan-dechets-2026/"

try:
    # Fetch the page
    driver.get(url)
    time.sleep(5)  # Wait for the page to load
    
    # Wait for pins to be present
    wait = WebDriverWait(driver, 10)
    pins = wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, "mapplic-pin")))
    
    # Store the collected data
    waste_data = []
    
    # Iterate through each pin
    for i, pin in enumerate(pins):
        try:
            # Get the data-location attribute
            location = pin.get_attribute("data-location")
            
            # Skip the pin with data-location="la-rochelle"
            if location in {"la-rochelle", "chatelaillon-plage"} :
                # Close the tooltip before clicking another pin
                try:
                    close_button = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "mapplic-tooltip-close")))
                    close_button.click()
                    time.sleep(0.5)
                except TimeoutException:
                    print(f"Pin {i} ({location}): No close button found, continuing...")
                print(f"Skipping pin {i} with location: {location}")
                continue
            
            # Scroll the element into view first
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", pin)
            time.sleep(0.5)
            
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
                time.sleep(0.5)
            except TimeoutException:
                print(f"Pin {i} ({location}): No close button found, continuing...")
            
            print(f"Pin {i} ({location}): Successfully extracted and closed data")
            
        except (ElementClickInterceptedException, TimeoutException) as e:
            print(f"Error processing pin {i} ({location}): {e}")
            continue
    
    # Close Selenium driver
    driver.quit()
    
    # Print results
    for data in waste_data:
        print(f"Location: {data['location']}")
        print(f"Data: {data['tooltip_content']}")
        print("---")
    
    print(f"Total pins processed (excluding La Rochelle): {len(waste_data)}")
    
except Exception as e:
    print(f"Error accessing the page: {e}")
    driver.quit()
