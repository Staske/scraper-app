from flask import Flask, jsonify
from flask_cors import CORS
import json
import os
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time

app = Flask(__name__)
CORS(app)  # Enable CORS for the entire app

MATCHES_FILE = 'matches.json'
ESPN_FILE = 'espn_posts.json'

def scrape_and_save_matches():
    # Initialize headless Chrome with webdriver-manager
    service = Service(ChromeDriverManager().install())
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    driver = webdriver.Chrome(service=service, options=options)

    # Open the flashscore website
    driver.get("https://www.flashscore.com/basketball/europe/euroleague/results/")

    try:
        # Wait for match data to load (home team elements)
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'event__participant--home'))
        )

        # Find all match elements
        matches = driver.find_elements(By.CLASS_NAME, 'event__match')
        match_data = []

        # Loop through matches and extract details
        for match in matches:
            home_team = match.find_element(By.CLASS_NAME, 'event__participant--home').text
            away_team = match.find_element(By.CLASS_NAME, 'event__participant--away').text

            score = match.find_elements(By.CLASS_NAME, 'event__score')
            if len(score) > 0:
                score_home = score[0].text
                score_away = score[1].text
            else:
                score_home = score_away = 'N/A'

            match_data.append({
                'home_team': home_team,
                'away_team': away_team,
                'score_home': score_home,
                'score_away': score_away
            })
    finally:
        driver.quit()

    # Save match data to JSON file
    with open(MATCHES_FILE, 'w') as f:
        json.dump(match_data, f)

def convert_relative_date(relative_date):
    """
    Convert a relative date string (like '11d', '5h', '30m', '15s') 
    into an absolute date/time string based on the current time.
    """
    now = datetime.now()
    try:
        if relative_date.endswith('d'):
            days = int(relative_date[:-1])
            full_date = now - timedelta(days=days)
        elif relative_date.endswith('h'):
            hours = int(relative_date[:-1])
            full_date = now - timedelta(hours=hours)
        elif relative_date.endswith('m'):
            minutes = int(relative_date[:-1])
            full_date = now - timedelta(minutes=minutes)
        elif relative_date.endswith('s'):
            seconds = int(relative_date[:-1])
            full_date = now - timedelta(seconds=seconds)
        else:
            full_date = now
        return full_date.strftime("%Y-%m-%d %H:%M:%S")
    except Exception as e:
        print("Error converting relative date:", e)
        return relative_date

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
                # Convert relative URL to absolute if needed
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

# Route to get flashscore matches, using the saved JSON if available
@app.route('/matches', methods=['GET'])
def get_matches():
    if os.path.exists(MATCHES_FILE):
        with open(MATCHES_FILE, 'r') as f:
            match_data = json.load(f)
    else:
        scrape_and_save_matches()
        with open(MATCHES_FILE, 'r') as f:
            match_data = json.load(f)
    return jsonify(match_data)

# Route to manually trigger flashscore matches scraping
@app.route('/scrape', methods=['GET'])
def scrape_matches():
    scrape_and_save_matches()
    return jsonify({"message": "Matches scraped and saved successfully."})

# Route to get ESPN posts, using the saved JSON if available
@app.route('/espn', methods=['GET'])
def get_espn_posts():
    if os.path.exists(ESPN_FILE):
        with open(ESPN_FILE, 'r') as f:
            posts = json.load(f)
    else:
        scrape_and_save_espn_posts()
        with open(ESPN_FILE, 'r') as f:
            posts = json.load(f)
    return jsonify(posts)

# Route to manually trigger ESPN posts scraping
@app.route('/espn-scrape', methods=['GET'])
def scrape_espn():
    scrape_and_save_espn_posts()
    return jsonify({"message": "ESPN posts scraped and saved successfully."})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
