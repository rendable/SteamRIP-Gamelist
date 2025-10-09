import json
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
    
def scrape_game_list():
    # ...
    print("Initializing browser...")
    try:
        options = uc.ChromeOptions()
        driver = uc.Chrome(options=options, version_main=140)
        
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
            # Optional: Print progress to the console
            # print(f"\rParsed game {index + 1}/{total_games}...", end="")

        print("\nParsing complete.")
        return scraped_games

    except TimeoutException:
        print("Error: Timed out waiting for the game list page to load.")
        return []
    except Exception as e:
        print(f"An unexpected error occurred during scraping: {e}")
        return []
    finally:
        if driver:
            print("Closing browser.")
            driver.quit()

def main():
    """Main function to run the scraper and save the results."""
    scraped_games = scrape_game_list()
    
    if not scraped_games:
        print("No games were scraped. Exiting without updating files.")
        return

    print(f"Successfully scraped {len(scraped_games)} games. Sorting and saving...")
    
    # Sort games alphabetically
    scraped_games.sort(key=lambda x: x['name'])
    
    # Save the main game list
    with open("links_reformatted.json", 'w', encoding='utf8') as f:
        json.dump(scraped_games, f, indent=4)
        
    # Save the update timestamp
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")
    with open("update_info.json", "w") as f:
        json.dump({"last_update": timestamp}, f)
        
    print("Files 'links_reformatted.json' and 'update_info.json' have been updated.")

if __name__ == "__main__":
    main()
