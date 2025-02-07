from flask import Flask, jsonify
from flask_cors import CORS
import json
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

app = Flask(__name__)
CORS(app)  # Enable CORS for the entire app

MATCHES_FILE = 'matches.json'

# Function to scrape and save the data to a file
def scrape_and_save_matches():
    # Initialize WebDriver (use webdriver-manager to automatically manage the driver)
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)

    # Open the website
    driver.get("https://www.flashscore.com/basketball/europe/euroleague/results/")

    # Wait for the page to load and find the match elements
    try:
        # Wait for the match data to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'event__participant--home'))
        )

        # Find all match elements
        matches = driver.find_elements(By.CLASS_NAME, 'event__match')

        match_data = []

        # Loop through all matches and extract the relevant information
        for match in matches:
            # Get the home and away teams
            home_team = match.find_element(By.CLASS_NAME, 'event__participant--home').text
            away_team = match.find_element(By.CLASS_NAME, 'event__participant--away').text

            # Get the score, if available
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
        # Close the driver after scraping
        driver.quit()

    # Save the scraped data to a JSON file
    with open(MATCHES_FILE, 'w') as f:
        json.dump(match_data, f)

# Route to get matches, loading from file if exists, else scraping
@app.route('/matches', methods=['GET'])
def get_matches():
    # Check if the matches file exists
    if os.path.exists(MATCHES_FILE):
        with open(MATCHES_FILE, 'r') as f:
            match_data = json.load(f)
    else:
        # If file doesn't exist, scrape and save data
        scrape_and_save_matches()
        with open(MATCHES_FILE, 'r') as f:
            match_data = json.load(f)
    
    return jsonify(match_data)

# Route to manually trigger scraping and update the file
@app.route('/scrape', methods=['GET'])
def scrape():
    scrape_and_save_matches()
    return jsonify({"message": "Data scraped and saved successfully."})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
