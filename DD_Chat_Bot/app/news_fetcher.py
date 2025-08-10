# app/news_fetcher.py

import feedparser
import requests
from datetime import datetime
from langchain.docstore.document import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from app.logging.logger import logger
from app.config import settings
from app.marketaux_client import marketaux_client
from newspaper import Article

def fetch_rss_news():
    """Fetch all news from Yahoo Finance RSS only, including article content"""
    sources = [
        "https://finance.yahoo.com/news/rssindex"
    ]
    all_news = []
    for url in sources:
        try:
            logger.info(f"Fetching from {url}")
            feed = feedparser.parse(url)
            for entry in feed.entries:
                if hasattr(entry, 'title') and hasattr(entry, 'link'):
                    article_content = ""
                    try:
                        article = Article(entry.link)
                        article.download()
                        article.parse()
                        article_content = article.text.strip()
                       
                    except Exception as e:
                        logger.warning(f"Failed to fetch article content from {entry.link}: {str(e)}")
                    news_item = {
                        "title": entry.title.strip(),
                        "summary": getattr(entry, 'summary', '').strip(),
                        "link": getattr(entry, 'link', ''),
                        "source": url,
                        "date": datetime.now().isoformat(),
                        "published": getattr(entry, 'published', ''),
                        "author": getattr(entry, 'author', ''),
                        "api_source": "rss",
                        "article_content": article_content
                    }
                      # Debugging line, remove in production
                    all_news.append(news_item)
            logger.info(f"Fetched {len(feed.entries)} articles from {url}")
        except Exception as e:
            logger.error(f"Error fetching from {url}: {str(e)}")
    return all_news

def fetch_marketaux_news():
    """Fetch all news from MarketAux API"""
    if not marketaux_client.is_available():
        logger.warning("MarketAux API not available, skipping MarketAux news fetch")
        return []
    try:
        logger.info("Fetching news from MarketAux...")
        general_news = marketaux_client.get_news_sentiment(limit=200)
        for item in general_news:
            item["api_source"] = "marketaux"
        logger.info(f"Fetched {len(general_news)} MarketAux articles")
        return general_news
    except Exception as e:
        logger.error(f"Error fetching MarketAux news: {str(e)}")
        return []

def fetch_combined_news():
    """Fetch all news from Yahoo Finance RSS and MarketAux"""
    rss_news = fetch_rss_news()
    marketaux_news = fetch_marketaux_news()
    combined_news = rss_news + marketaux_news
    # Remove duplicates by title
    unique_news = []
    seen_titles = set()
    for item in combined_news:
        title_lower = item["title"].lower().strip()
        if title_lower not in seen_titles :
            seen_titles.add(title_lower)
            #import pdb; pdb.set_trace()  # Debugging line, remove in production
            unique_news.append(item)
    logger.info(f"Combined unique news count: {len(unique_news)}")
    return unique_news

def filter_and_clean_news(news_items):
    """Basic cleaning for news items"""
    filtered_news = []
    for item in news_items:
        if len(item["summary"]) < 50:
            continue
        import re
        clean_summary = re.sub(r'<[^>]+>', '', item["summary"])
        clean_summary = re.sub(r'\s+', ' ', clean_summary).strip()
        item["summary"] = clean_summary
        filtered_news.append(item)
    logger.info(f"Cleaned {len(filtered_news)} articles")
    return filtered_news

def process_and_store(news_items):
    """Process and store all news items in the vector database"""
    if not news_items:
        logger.warning("No news items to process")
        return
    #filtered_news = filter_and_clean_news(news_items)
    docs = []
    #import pdb; pdb.set_trace()
    for item in news_items:
        # Prefer article_content if available, otherwise use summary
        article_text = item.get("article_content", "").strip()
        if article_text:
            content = f"Title: {item['title']}\n\nArticle: {article_text}\nSource: {item['source']}"
        else:
            content = f"Title: {item['title']}\n\nSummary: {item['summary']}\nSource: {item['source']}"
        metadata = {
            "title": item["title"],
            "summary": item["summary"],
            "link": item["link"],
            "source": item["source"],
            "date": item["date"],
            "published": item.get("published", ""),
            "author": item.get("author", ""),
            "api_source": item.get("api_source", "rss"),
            "article_content": article_text  # Store full article content in metadata
        }
          # Debugging line, remove in production
        doc = Document(page_content=content, metadata=metadata)
        docs.append(doc)
    try:
        splitter = RecursiveCharacterTextSplitter(chunk_size=1200, chunk_overlap=150, length_function=len)
        chunks = splitter.split_documents(docs)
        embedder = HuggingFaceEmbeddings(model_name=settings.EMBED_MODEL)
        vectorstore = Chroma.from_documents(documents=chunks, embedding=embedder, persist_directory=settings.CHROMA_PATH)
        vectorstore.persist()
        logger.info(f"Stored {len(chunks)} document chunks into vector store")
    except Exception as e:
        logger.error(f"Error processing and storing news: {str(e)}")

def get_news_statistics():
    """Get statistics about the stored news"""
    try:
        embedder = HuggingFaceEmbeddings(model_name=settings.EMBED_MODEL)
        vectorstore = Chroma(persist_directory=settings.CHROMA_PATH, embedding_function=embedder)
        collection = vectorstore._collection
        count = collection.count()
        logger.info(f"Vector store contains {count} documents")
        return {"total_documents": count}
    except Exception as e:
        logger.error(f"Error getting news statistics: {str(e)}")
        return {"error": str(e)}

if __name__ == "__main__":
    logger.info("Starting combined news fetching and processing...")
    news = fetch_combined_news()
    process_and_store(news)
    get_news_statistics()
    logger.info("Combined news processing completed!")
