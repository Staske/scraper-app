import json
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time

from utils.date_utils import convert_relative_date

ESPN_FILE = 'espn_posts.json'

def scrape_espn_posts():
    # Initialize headless Chrome with webdriver-manager
    service = Service(ChromeDriverManager().install())
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    driver = webdriver.Chrome(service=service, options=options)

    driver.get("https://www.espn.com/contributor/shams-charania")
    try:
        # Wait for the ESPN posts to load using the data-testid attribute
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//*[@data-testid='contributorCardWrapper']"))
        )
        # Find all post containers
        cards = driver.find_elements(By.XPATH, "//*[@data-testid='contributorCardWrapper']")
        posts = []

        for card in cards:
            try:
                # Extract contributor header info
                header = card.find_element(By.XPATH, ".//*[@data-testid='contributorCardHeader']")
                contributor_name = header.find_element(By.TAG_NAME, "h2").text

                # The relative date is assumed to be in the second span with class containing 'FWLyZ'
                spans = header.find_elements(By.XPATH, ".//span[contains(@class, 'FWLyZ')]")
                relative_date = spans[1].text if len(spans) > 1 else ""
                full_date = convert_relative_date(relative_date)

                # Extract main post details from the layout card section
                layout_section = card.find_element(By.XPATH, ".//*[@data-testid='prism-LayoutCard']")
                link_tag = layout_section.find_element(By.XPATH, ".//a[@data-testid='prism-linkbase']")
                post_url = link_tag.get_attribute("href")
                if post_url.startswith("/"):
                    post_url = "https://www.espn.com" + post_url

                try:
                    text_element = link_tag.find_element(By.XPATH, ".//span[@data-testid='prism-Text']")
                    post_text = text_element.text
                except Exception:
                    post_text = ""

                posts.append({
                    "contributor": contributor_name,
                    "relative_date": relative_date,
                    "full_date": full_date,
                    "text": post_text,
                    "url": post_url
                })
            except Exception as e:
                print("Error processing a card:", e)
                continue
    finally:
        driver.quit()

    return posts

def scrape_and_save_espn_posts():
    posts = scrape_espn_posts()
    with open(ESPN_FILE, 'w') as f:
        json.dump(posts, f)
