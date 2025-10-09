import json
import os # Import the 'os' module to read environment variables
from datetime import datetime
import undetected_chromedriver as uc
from bs4 import BeautifulSoup
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def scrape_game_list():
    """Scrapes the main game list from SteamRIP and returns a list of game dictionaries."""
    
    url_to_scrape = "https://steamrip.com/games-list-page/"
    scraped_games = []
    driver = None
    
    print("Initializing browser...")
    try:
        options = uc.ChromeOptions()
        
        # --- THE DEFINITIVE FIX ---
        # 1. Get the path to the browser executable installed by the workflow
        browser_path = os.environ.get("CHROME_PATH")
        print(f"Detected CHROME_PATH: {browser_path}")

        if not browser_path:
            raise ValueError("CHROME_PATH environment variable not set. Cannot find browser.")

        # 2. Pass the exact browser path and the matching version to the driver
        driver = uc.Chrome(
            browser_executable_path=browser_path, 
            version_main=143,
            options=options
        )
        
        print(f"Navigating to {url_to_scrape}...")
        driver.get(url_to_scrape)
        
        print("Waiting for page content to load (max 60 seconds)...")
        wait = WebDriverWait(driver, 60)
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.az-link-posts-block")))
        
        print("Page loaded. Parsing game links...")
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        game_links = soup.select("div.az-list-container li a")
        
        if not game_links:
            print("Error: Found the main container, but no game links were inside.")
            return []
            
        total_games = len(game_links)
        print(f"Found {total_games} games. Extracting details...")
        
        for index, link_tag in enumerate(game_links):
            relative_url = link_tag['href']
            game_name = link_tag.get_text(strip=True)
            full_url = f"https://steamrip.com{relative_url}"
            scraped_games.append({"name": game_name, "url": full_url, "download_links": {}})

        print("\nParsing complete.")
        return scraped_games

    except Exception as e:
        print(f"An unexpected error occurred during scraping: {e}")
        # Re-raising the error will cause the workflow to fail, which is better for debugging
        raise

    finally:
        if driver:
            print("Closing browser.")
            driver.quit()

def main():
    """Main function to run the scraper and save the results."""
    try:
        scraped_games = scrape_game_list()
    except Exception as e:
        print(f"Scraper failed with an unhandled exception: {e}")
        # Force the script to exit with a non-zero code to make the workflow step fail
        exit(1)

    if not scraped_games:
        print("No games were scraped. Exiting without updating files.")
        return

    print(f"Successfully scraped {len(scraped_games)} games. Sorting and saving...")
    
    scraped_games.sort(key=lambda x: x['name'])
    
    with open("links_reformatted.json", 'w', encoding='utf8') as f:
        json.dump(scraped_games, f, indent=4)
        
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")
    with open("update_info.json", "w") as f:
        json.dump({"last_update": timestamp}, f)
        
    print("Files 'links_reformatted.json' and 'update_info.json' have been updated.")

if __name__ == "__main__":
    main()
