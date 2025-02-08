import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta

def convert_relative_date(relative_date):
    """
    Convert a relative date string (like '11d', '5h', '30m', etc.)
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
            # If no unit is found, return current time as fallback.
            full_date = now
        return full_date.strftime("%Y-%m-%d %H:%M:%S")
    except Exception as e:
        print("Error converting relative date:", e)
        return relative_date

def scrape_shams_charania_posts():
    url = "https://www.espn.com/contributor/shams-charania"
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/87.0.4280.66 Safari/537.36"
        )
    }
    
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"Failed to retrieve page: HTTP {response.status_code}")
        return []
    
    soup = BeautifulSoup(response.text, "html.parser")
    
    # Look for the contributor post containers using the data-testid attribute.
    cards = soup.find_all("div", {"data-testid": "contributorCardWrapper"})
    posts = []
    
    for card in cards:
        # Extract contributor and relative date information from the header.
        header = card.find("div", {"data-testid": "contributorCardHeader"})
        if header:
            name_tag = header.find("h2")
            contributor_name = name_tag.get_text(strip=True) if name_tag else ""
            # Assuming the second <span> with class "FWLyZ" holds the relative date (e.g., "11d")
            spans = header.find_all("span", class_="FWLyZ")
            relative_date = spans[1].get_text(strip=True) if len(spans) > 1 else ""
            # Convert the relative date to a full date.
            full_date = convert_relative_date(relative_date)
        else:
            contributor_name = ""
            relative_date = ""
            full_date = ""
        
        # Extract the main post content and URL from the layout card.
        layout_section = card.find("section", {"data-testid": "prism-LayoutCard"})
        if layout_section:
            link_tag = layout_section.find("a", {"data-testid": "prism-linkbase"})
            if link_tag:
                post_url = link_tag.get("href", "")
                if post_url.startswith("/"):
                    post_url = "https://www.espn.com" + post_url
                
                text_tag = link_tag.find("span", {"data-testid": "prism-Text"})
                post_text = text_tag.get_text(strip=True) if text_tag else ""
                
                posts.append({
                    "contributor": contributor_name,
                    "relative_date": relative_date,
                    "full_date": full_date,
                    "text": post_text,
                    "url": post_url,
                })
    
    return posts

if __name__ == "__main__":
    posts = scrape_shams_charania_posts()
    if posts:
        for post in posts:
            print("Contributor:", post["contributor"])
            print("Relative Date:", post["relative_date"])
            print("Full Date:", post["full_date"])
            print("URL:", post["url"])
            print("Text:", post["text"])
            print("-" * 50)
    else:
        print("No posts found.")
