import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
import time
import sqlite3

class YahooNewsScraper:
    def __init__(self):
        self.base_url = "https://finance.yahoo.com/topic/stock-market-news/"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

    def get_news_articles(self):
        try:
            # Send GET request to the URL
            response = requests.get(self.base_url, headers=self.headers)
            response.raise_for_status()  # Raise an exception for bad status codes
            
            # Parse the HTML content
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find all news articles
            articles = []
            news_items = soup.find_all('li', class_='stream-item story-item yf-1usaaz9')
            
            for item in news_items:
                article = {}
                
                # Get article title
                title_element = item.find('h3')
                if title_element:
                    article['title'] = title_element.text.strip()
                
                # Get article link
                link_element = item.find('a')
                if link_element:
                    article['link'] = 'https://finance.yahoo.com' + link_element.get('href', '')
                
                # Get article source and time
                source_time = item.find('div', class_='publishing yf-1weyqlp')
                if source_time:
                    source_time_text = source_time.text.strip()
                    source_time_parts = source_time_text.split('•')
                    if len(source_time_parts) >= 2:
                        article['source'] = source_time_parts[0].strip()
                        article['time'] = source_time_parts[1].strip()
                
                # Get article summary
                summary = item.find('p')
                if summary:
                    article['summary'] = summary.text.strip()

                # Get article img link
                img_link = item.find('img')
                if img_link:
                    article['src'] = img_link.get('src', '')
                
                if article:  # Only append if we found some content
                    articles.append(article)
            
            return articles

        except requests.RequestException as e:
            print(f"Error fetching data: {e}")
            return []

    def save_to_json(self, articles, filename='records.json'):
        """Save the scraped articles to a JSON file"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump({
                    'timestamp': datetime.now().isoformat(),
                    'articles': articles
                }, f, indent=2, ensure_ascii=False)
            print(f"Data saved to {filename}")
        except Exception as e:
            print(f"Error saving to JSON: {e}")

    def save_to_sqlite(self, articles, db_name='records.db'):
        """
        Save the scraped articles to an SQLite database.
        """
        try:
            # Connect to SQLite database (or create it if it doesn't exist)
            conn = sqlite3.connect(db_name)
            cursor = conn.cursor()

            # Create table if it doesn't exist
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS articles (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT,
                    link TEXT,
                    source TEXT,
                    time TEXT,
                    summary TEXT,
                    src TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            # Insert each article into the database
            for article in articles:
                cursor.execute('''
                    INSERT INTO articles (title, link, source, time, summary, src)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    article.get('title', ''),
                    article.get('link', ''),
                    article.get('source', ''),
                    article.get('time', ''),
                    article.get('summary', ''),
                    article.get('src', '')
                ))

            # Commit changes and close connection
            conn.commit()
            conn.close()
            print(f"Data saved to SQLite database: {db_name}")
        
        except Exception as e:
            print(f"Error saving to SQLite: {e}")

def main():
    scraper = YahooNewsScraper()
    articles = scraper.get_news_articles()
    
    if articles:
        print(f"Found {len(articles)} articles")
        scraper.save_to_json(articles)
        scraper.save_to_sqlite(articles)
        
        # Print the first 2 articles as a sample
        print("\nSample of first 2 articles:")
        for i, article in enumerate(articles[:2], 1):
            print(f"\nArticle {i}:")
            for key, value in article.items():
                print(f"{key}: {value}")
    else:
        print("No articles found")

if __name__ == "__main__":
    main() 