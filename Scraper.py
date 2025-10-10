import json
import os
import undetected_chromedriver as uc
from bs4 import BeautifulSoup
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def scrape_games():
    """Scrapes the game list and returns it as a list of dicts."""
    url_to_scrape = "https://steamrip.com/games-list-page/"
    scraped_games = []
    driver = None
    print("Initializing browser for scraping...")

    try:
        options = uc.ChromeOptions()
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        
        # --- THE DEFINITIVE FIX ---
        # 1. Read the exact browser version passed in from the workflow
        browser_version_str = os.environ.get("CHROME_VERSION")
        if not browser_version_str:
            raise ValueError("CHROME_VERSION environment variable not set.")
            
        # 2. Extract the major version number (e.g., 140 from "140.0.7339.0")
        major_version = int(browser_version_str.split('.')[0])
        print(f"Detected Chrome major version: {major_version}")

        # 3. Pass this exact version to undetected-chromedriver
        driver = uc.Chrome(options=options, version_main=major_version)
        
        print(f"Navigating to {url_to_scrape}...")
        driver.get(url_to_scrape)
        
        print("Waiting for Cloudflare and page content (max 120 seconds)...")
        wait = WebDriverWait(driver, 120) 
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.az-link-posts-block")))
        
        print("Page loaded. Parsing game list...")
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        game_links = soup.select("div.az-list-container li a")
        
        if not game_links:
            print("Error: Found the container, but no game links were inside.")
            return None

        total_games = len(game_links)
        print(f"Found {total_games} games. Extracting data...")

        for link_tag in game_links:
            relative_url = link_tag['href']
            full_url = f"https://steamrip.com{relative_url}"
            game_name = link_tag.get_text(strip=True)
            scraped_games.append({"name": game_name, "url": full_url, "download_links": {}})
        
        print("Data extraction complete.")
        return scraped_games

    except Exception as e:
        print(f"An unexpected error occurred during scraping: {e}")
        raise

    finally:
        if driver:
            print("Closing browser.")
            driver.quit()

if __name__ == "__main__":
    games = None
    try:
        games = scrape_games()
    except Exception as e:
        print(f"Scraper failed with an unhandled exception: {e}")
        exit(1)

    if games is not None:
        print(f"Successfully scraped {len(games)} games. Sorting and saving...")
        games.sort(key=lambda x: x['name'])
        with open("links_reformatted.json", "w", encoding="utf8") as f:
            json.dump(games, f, indent=4)
        print("Successfully saved game list to links_reformatted.json.")
    else:
        print("Scraping failed or returned no games. No file was written.")
        exit(1)
