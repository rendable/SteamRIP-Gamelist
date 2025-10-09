# scraper.py
import json
import time
import undetected_chromedriver as uc
from bs4 import BeautifulSoup
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

def scrape_games():
    """Scrapes the game list and returns it as a list of dicts."""
    url_to_scrape = "https://steamrip.com/games-list-page/"
    scraped_games = []
    driver = None
    print("Initializing browser for scraping...")

    try:
        options = uc.ChromeOptions()
        options.add_argument('--headless=new')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        driver = uc.Chrome(options=options)
        
        print(f"Navigating to {url_to_scrape}...")
        driver.get(url_to_scrape)
        
        print("Waiting for Cloudflare and page content...")
        # Wait up to 2 minutes for the main container to appear
        wait = WebDriverWait(driver, 120) 
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.az-link-posts-block")))
        
        print("Page loaded. Parsing game list...")
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        game_links = soup.select("div.az-list-container li a")
        
        if not game_links:
            print("Error: Found the container, but no game links were inside.")
            return []

        total_games = len(game_links)
        print(f"Found {total_games} games. Extracting data...")

        for link_tag in game_links:
            relative_url = link_tag['href']
            full_url = f"https://steamrip.com{relative_url}"
            game_name = link_tag.get_text(strip=True)
            # Each game entry will have an empty download_links field, as expected
            scraped_games.append({"name": game_name, "url": full_url, "download_links": {}})
        
        print("Data extraction complete.")
        return scraped_games

    except TimeoutException:
        print("FATAL: Timed out waiting for page content. The site structure may have changed or the server is slow.")
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None
    finally:
        if driver:
            driver.quit()
            print("Browser closed.")

if __name__ == "__main__":
    games = scrape_games()
    if games is not None:
        games.sort(key=lambda x: x['name'])
        with open("links_reformatted.json", "w", encoding="utf8") as f:
            json.dump(games, f, indent=4)
        print(f"Successfully scraped and saved {len(games)} games to links_reformatted.json.")
    else:
        print("Scraping failed. No file was written.")
        # Exit with a non-zero status code to indicate failure to the GitHub Action
        exit(1)
