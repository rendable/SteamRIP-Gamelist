# Scraper.py

import time
import json
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import chromedriver_py # This is the package we installed

def run_scraper():
    print("Initializing browser for scraping...")

    # --- WebDriver Setup ---
    # This is the new, required setup to make Selenium use the driver we manually installed.
    service = Service(executable_path=chromedriver_py.binary_path)

    # These options are crucial for running in a GitHub Action (a "headless" environment)
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("window-size=1920,1080") # Set a reasonable window size

    # Initialize the driver using both the service and the options
    driver = webdriver.Chrome(service=service, options=options)

    try:
        # --- YOUR SCRAPING LOGIC GOES HERE ---
        # This is an example. Replace it with your actual scraping code.
        
        print("Navigating to the target URL...")
        driver.get("https://steamrip.com/") # Example URL

        # Wait for the page to load (a simple sleep is okay for demonstration)
        time.sleep(5)

        print("Extracting data...")
        # Example: Find all game links on the homepage
        game_elements = driver.find_elements(By.CSS_SELECTOR, "a.card-post")
        
        scraped_data = []
        for element in game_elements:
            title = element.get_attribute("title")
            link = element.get_attribute("href")
            if title and link:
                scraped_data.append({"title": title, "link": link})

        if not scraped_data:
            raise Exception("No data was scraped. The website structure may have changed.")

        print(f"Successfully scraped {len(scraped_data)} items.")

        # --- SAVING THE FILE ---
        # This is an example of how to save the data to a JSON file.
        output_filename = "links_reformatted.json" # Make sure this matches your workflow's commit step
        with open(output_filename, 'w') as f:
            json.dump(scraped_data, f, indent=4)
        
        print(f"Data successfully saved to {output_filename}")


    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        # Re-raise the exception to make the GitHub Action fail as expected
        raise

    finally:
        # --- IMPORTANT: Clean up the browser session ---
        # This ensures the browser closes properly, even if an error occurs.
        print("Closing the browser.")
        driver.quit()

if __name__ == "__main__":
    run_scraper()
