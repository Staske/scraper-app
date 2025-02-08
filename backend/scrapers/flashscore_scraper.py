import json
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

MATCHES_FILE = 'matches.json'

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
