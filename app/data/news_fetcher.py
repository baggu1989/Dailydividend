import os
import requests
from dotenv import load_dotenv
from datetime import datetime

import feedparser
from datetime import datetime

load_dotenv()
API_KEY = os.getenv("NEWS_API_KEY")
class News:

    def fetch_marketaux_news(self,limit=5, symbols="AAPL,TSLA,GOOGL", language="en"):
        url = "https://api.marketaux.com/v1/news/all"
        params = {
            "api_token": API_KEY,
            "symbols": symbols,
            "language": language,
            "limit": limit,
            "filter_entities": "true"
        }

        response = requests.get(url, params=params)

        if response.status_code != 200:
            print("Error fetching news:", response.text)
            return []

        articles = response.json().get("data", [])
        
        news_list = []
        for item in articles:
            news_dict = {
                "title": item.get("title", "No Title"),
                "description": item.get("description", "No description available."),
                "date": item.get("published_at", "")[:10],
                "link": item.get("url", "#")
            }
            news_list.append(news_dict)
        
        return news_list


    def fetch_yahoo_financial_headlines(self,limit=10):
        rss_url = "https://finance.yahoo.com/news/rssindex"
        feed = feedparser.parse(rss_url)

        articles = []
        for entry in feed.entries[:limit]:
            published_date = None
            if hasattr(entry, "published_parsed") and entry.published_parsed:
                published_date = datetime(*entry.published_parsed[:6]).strftime('%Y-%m-%d')
            else:
                published_date = getattr(entry, "published", "Unknown")
            description = getattr(entry, "summary", getattr(entry, "title", "No description available."))
            articles.append({
                'title': entry.title,
                'description': description,
                'date': published_date,
                'link': entry.link
            })

        return articles


if __name__ == "__main__":
    # Your code here
    news = News()
    news_data = news.fetch_marketaux_news() + news.fetch_yahoo_financial_headlines()
    for news_item in news_data:
        print(news_item)
        print()
