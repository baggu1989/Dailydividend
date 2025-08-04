# app/marketaux_client.py

import requests
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
from app.logging.logger import logger
from app.config import settings

class MarketAuxClient:
    """Client for interacting with MarketAux API for financial news and sentiment analysis"""
    
    def __init__(self):
        self.api_key = settings.MARKETAUX_API_KEY
        self.base_url = "https://api.marketaux.com/v1"
        
        if not self.api_key:
            logger.warning("MarketAux API key not found. MarketAux features will be disabled.")
    
    def is_available(self) -> bool:
        """Check if MarketAux API is available"""
        return bool(self.api_key)
    
    def get_news_sentiment(self, symbols: List[str] = None, countries: List[str] = None, 
                          topics: List[str] = None, limit: int = 50) -> List[Dict]:
        """
        Get news with sentiment analysis from MarketAux
        
        Args:
            symbols: List of stock symbols to filter by
            countries: List of countries to filter by
            topics: List of topics to filter by
            limit: Maximum number of articles to return
        """
        if not self.is_available():
            logger.warning("MarketAux API not available")
            return []
        
        try:
            params = {
                'api_token': self.api_key,
                'limit': limit,
                'language': 'en'
            }
            
            if symbols:
                params['symbols'] = ','.join(symbols)
            if countries:
                params['countries'] = ','.join(countries)
            if topics:
                params['topics'] = ','.join(topics)
            
            response = requests.get(f"{self.base_url}/news/all", params=params)
            response.raise_for_status()
            
            data = response.json()
            articles = data.get('data', [])
            
            processed_articles = []
            for article in articles:
                processed_article = self._process_article(article)
                if processed_article:
                    processed_articles.append(processed_article)
            
            logger.info(f"Retrieved {len(processed_articles)} articles from MarketAux")
            return processed_articles
            
        except Exception as e:
            logger.error(f"Error fetching news from MarketAux: {str(e)}")
            return []
    
    def get_news_by_symbol(self, symbol: str, limit: int = 20) -> List[Dict]:
        """Get news specifically for a stock symbol"""
        return self.get_news_sentiment(symbols=[symbol], limit=limit)
    
    def get_market_sentiment(self, symbols: List[str]) -> Dict[str, Any]:
        """
        Get market sentiment for specific symbols
        
        Args:
            symbols: List of stock symbols
        """
        if not self.is_available():
            logger.warning("MarketAux API not available")
            return {}
        
        try:
            params = {
                'api_token': self.api_key,
                'symbols': ','.join(symbols)
            }
            
            response = requests.get(f"{self.base_url}/news/sentiment", params=params)
            response.raise_for_status()
            
            data = response.json()
            return data
            
        except Exception as e:
            logger.error(f"Error fetching market sentiment from MarketAux: {str(e)}")
            return {}
    
    def get_entity_sentiment(self, entity: str) -> Dict[str, Any]:
        """
        Get sentiment analysis for a specific entity (company, topic, etc.)
        
        Args:
            entity: Entity name to analyze
        """
        if not self.is_available():
            logger.warning("MarketAux API not available")
            return {}
        
        try:
            params = {
                'api_token': self.api_key,
                'entities': entity
            }
            
            response = requests.get(f"{self.base_url}/news/sentiment", params=params)
            response.raise_for_status()
            
            data = response.json()
            return data
            
        except Exception as e:
            logger.error(f"Error fetching entity sentiment from MarketAux: {str(e)}")
            return {}
    
    def get_trending_topics(self, countries: List[str] = None) -> List[Dict]:
        """Get trending topics in financial news"""
        if not self.is_available():
            logger.warning("MarketAux API not available")
            return []
        
        try:
            params = {
                'api_token': self.api_key
            }
            
            if countries:
                params['countries'] = ','.join(countries)
            
            response = requests.get(f"{self.base_url}/news/topics", params=params)
            response.raise_for_status()
            
            data = response.json()
            return data.get('data', [])
            
        except Exception as e:
            logger.error(f"Error fetching trending topics from MarketAux: {str(e)}")
            return []
    
    def _process_article(self, article: Dict) -> Optional[Dict]:
        """Process a raw article from MarketAux API without topic or stock filtering"""
        try:
            title = article.get('title', '')
            description = article.get('description', '')
            url = article.get('url', '')
            published_at = article.get('published_at', '')

            sentiment = article.get('sentiment', {})
            sentiment_score = sentiment.get('score', 0)
            sentiment_label = sentiment.get('label', 'neutral')

            processed_article = {
                "title": title,
                "summary": description,
                "link": url,
                "source": "MarketAux",
                "date": datetime.now().isoformat(),
                "published": published_at,
                "sentiment_score": sentiment_score,
                "sentiment_label": sentiment_label,
                "api_source": "marketaux"
            }

            return processed_article

        except Exception as e:
            logger.error(f"Error processing MarketAux article: {str(e)}")
            return None
    
    def _categorize_topic(self, topics: List[str], symbols: List[str]) -> str:
        """Categorize the article based on topics and symbols"""
        if symbols:
            return "stocks"
        
        topic_lower = [topic.lower() for topic in topics]
        
        if any(topic in ["commodities", "oil", "gold", "silver", "copper"] for topic in topic_lower):
            return "commodities"
        elif any(topic in ["forex", "currency", "fx"] for topic in topic_lower):
            return "forex"
        elif any(topic in ["economy", "gdp", "inflation", "recession"] for topic in topic_lower):
            return "economy"
        else:
            return "market"
    
    def get_enhanced_news_summary(self, symbol: str = None, topic: str = None) -> Dict[str, Any]:
        """
        Get enhanced news summary with sentiment analysis
        
        Args:
            symbol: Optional stock symbol to focus on
            topic: Optional topic to focus on
        """
        if not self.is_available():
            return {"error": "MarketAux API not available"}
        
        try:
            # Get news articles
            if symbol:
                articles = self.get_news_by_symbol(symbol, limit=30)
            elif topic:
                articles = self.get_news_sentiment(topics=[topic], limit=30)
            else:
                articles = self.get_news_sentiment(limit=30)
            
            if not articles:
                return {"error": "No articles found"}
            
            # Calculate sentiment statistics
            sentiment_scores = [article.get('sentiment_score', 0) for article in articles]
            avg_sentiment = sum(sentiment_scores) / len(sentiment_scores) if sentiment_scores else 0
            
            # Count sentiment labels
            sentiment_counts = {}
            for article in articles:
                label = article.get('sentiment_label', 'neutral')
                sentiment_counts[label] = sentiment_counts.get(label, 0) + 1
            
            # Get most mentioned symbols
            all_symbols = []
            for article in articles:
                all_symbols.extend(article.get('mentioned_symbols', []))
            
            symbol_counts = {}
            for symbol in all_symbols:
                symbol_counts[symbol] = symbol_counts.get(symbol, 0) + 1
            
            top_symbols = sorted(symbol_counts.items(), key=lambda x: x[1], reverse=True)[:10]
            
            return {
                "total_articles": len(articles),
                "average_sentiment": avg_sentiment,
                "sentiment_distribution": sentiment_counts,
                "top_mentioned_symbols": top_symbols,
                "articles": articles[:10]  # Return first 10 articles
            }
            
        except Exception as e:
            logger.error(f"Error getting enhanced news summary: {str(e)}")
            return {"error": str(e)}

# Global instance
marketaux_client = MarketAuxClient()