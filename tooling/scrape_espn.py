from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time
from bs4 import BeautifulSoup

def scrape_shams_charania_tweets():
    # URL for Shams Charania’s ESPN press room page
    url = "https://espnpressroom.com/us/bios/shams-charania/"
    
    # Configure Selenium to use a headless Chrome browser.
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    
    # Initialize the webdriver (make sure you have the appropriate chromedriver installed)
    driver = webdriver.Chrome(options=options)
    
    # Open the page and wait for JavaScript to load dynamic content.
    driver.get(url)
    # Increase sleep time if necessary or use WebDriverWait for a more robust solution.
    time.sleep(5)
    
    # Get the fully rendered page source and parse it with BeautifulSoup.
    html = driver.page_source
    soup = BeautifulSoup(html, "html.parser")
    
    # Look for article tags that might contain tweets.
    tweet_articles = soup.find_all("article")
    tweets = []
    
    for article in tweet_articles:
        # Look for an element with data-testid="tweetText"
        tweet_text_elem = article.find(attrs={"data-testid": "tweetText"})
        if tweet_text_elem:
            tweet_text = tweet_text_elem.get_text(strip=True)
            # Optionally, extract the timestamp if available.
            time_elem = article.find("time")
            tweet_time = time_elem["datetime"] if time_elem and time_elem.has_attr("datetime") else None
            # Extract a tweet URL (if a link to the tweet is present).
            tweet_link_elem = article.find("a", href=lambda x: x and "twitter.com/ShamsCharania/status" in x)
            tweet_url = tweet_link_elem["href"] if tweet_link_elem else None

            tweets.append({
                "text": tweet_text,
                "time": tweet_time,
                "url": tweet_url
            })

    driver.quit()
    return tweets

if __name__ == "__main__":
    tweets = scrape_shams_charania_tweets()
    if tweets:
        for tweet in tweets:
            print("Tweet:", tweet["text"])
            print("Time:", tweet["time"])
            print("URL:", tweet["url"])
            print("-" * 40)
    else:
        print("No tweets found on the page.")
