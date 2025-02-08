from flask import Flask, jsonify
from flask_cors import CORS
import json
import os

from scrapers.flashscore_scraper import scrape_and_save_matches
from scrapers.espn_scraper import scrape_and_save_espn_posts

app = Flask(__name__)
CORS(app)  # Enable CORS for the entire app

MATCHES_FILE = 'matches.json'
ESPN_FILE = 'espn_posts.json'

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
