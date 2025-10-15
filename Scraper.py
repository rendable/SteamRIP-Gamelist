# File: Scraper.py (Proxy-less Version)

import time
import random
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager

options = webdriver.ChromeOptions()

options.add_argument("--start-maximized")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--disable-blink-features=AutomationControlled")

options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option('useAutomationExtension', False)

user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36"
options.add_argument(f'user-agent={user_agent}')


driver = None
try:
    print("Initializing browser for scraping...")

    service = ChromeService(executable_path=ChromeDriverManager().install())
    
    driver = webdriver.Chrome(service=service, options=options)
    
    print("Browser initialized successfully.")
    
    target_url = "https://steamrip.com/games-list-page/"
    print(f"Navigating to {target_url}...")
    driver.get(target_url)

    print("Performing human-like actions...")
    time.sleep(random.uniform(4.1, 7.3))

    scroll_height = driver.execute_script("return document.body.scrollHeight")
    if scroll_height > 0:
        random_scroll_amount = random.randint(int(scroll_height * 0.2), int(scroll_height * 0.5))
        driver.execute_script(f"window.scrollTo(0, {random_scroll_amount});")
        print(f"Scrolled down by {random_scroll_amount} pixels.")
        time.sleep(random.uniform(2.5, 4.8))

    print("Scraping logic starting...")
    page_title = driver.title
    print(f"Successfully loaded page. Title: '{page_title}'")
    
    if "Cloudflare" in page_title or "Just a moment..." in page_title or "Access denied" in page_title:
        print("\nWARNING: Page title suggests we may have been blocked by Cloudflare.")
        
    screenshot_file = "final_page_screenshot.png"
    driver.save_screenshot(screenshot_file)
    print(f"Screenshot saved to '{screenshot_file}'.")

except Exception as e:
    print(f"\nAn unexpected error occurred during scraping: {e}")
    if driver:
        driver.save_screenshot("error_screenshot.png")
        print("Error screenshot saved.")
    exit(1)

finally:
    if driver:
        print("Closing browser.")
        driver.quit()
