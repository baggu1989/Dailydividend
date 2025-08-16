import sys
import os
import requests
import logging

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from backend.scheduler.prompts import DAILY_PROMPT
from backend.scheduler.llms.Groqllm import Groq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from data.news_fetcher import News
from datetime import datetime
from data.stock_news import get_index_change
import json


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

class DAILY_NEWS:
    def __init__(self):
        try:
            groq_instance = Groq()          
            self.llm = groq_instance.get_llm()  
            logger.info("LLM initialized successfully.")
        except Exception as e:
            logger.error(f"Failed to initialize LLM: {e}")
            raise RuntimeError(f"Failed to initialize LLM: {e}")
        self.prompt = DAILY_PROMPT
        self.news = News()

    def combine_news(self, news_list):
        combined = ""
        for item in news_list:
            combined += f"""📰 {item['title']}
📅 {item['date']}
📄 {item['description']}
🔗 {item['link']}

"""
        return combined.strip()

    def get_news(self):
        today = datetime.today()
        day = today.strftime("%A")
        month = today.strftime("%B")
        date = today.strftime("%d")
        
        # Get market data
        sp500_change = get_index_change("^GSPC")
        eurostoxx_change = get_index_change("^STOXX50E")
        ftse100_change = get_index_change("^FTSE")
        
        sp500_change = float(sp500_change) if sp500_change is not None else 0.0
        eurostoxx_change = float(eurostoxx_change) if eurostoxx_change is not None else 0.0
        ftse100_change = float(ftse100_change) if ftse100_change is not None else 0.0
        
        logger.info(f"Market data being passed to LLM - S&P: {sp500_change:.1f}%, EUROSTOXX: {eurostoxx_change:.1f}%, FTSE: {ftse100_change:.1f}%")
        
        news_list = self.news.fetch_marketaux_news() + self.news.fetch_yahoo_financial_headlines()
        news = self.combine_news(news_list[:13])

        if not self.llm:
            logger.error("LLM is not initialized.")
            raise RuntimeError("LLM is not initialized.")
        
        try:
            prompt = ChatPromptTemplate.from_messages([
                ('system', self.prompt),
                ('human', f"""Here are the top financial news and REAL market data:

ACTUAL MARKET DATA (USE THESE EXACT VALUES):
- S&P 500: {sp500_change:+.1f}%
- EUROSTOXX 50: {eurostoxx_change:+.1f}%  
- FTSE 100: {ftse100_change:+.1f}%

FINANCIAL NEWS:
{news}

IMPORTANT: Use the ACTUAL market data provided above, do NOT make up your own market numbers.""")
            ])
            chain = prompt | self.llm | StrOutputParser()
            response = chain.invoke({
                'Day': day,
                'Month': month,
                'Date': date,
                'SP_change': sp500_change,
                'Eurostoxx_change': eurostoxx_change,
                'FTSE_change': ftse100_change,
            })

            # Validation for completeness
            if not response or len(response.strip()) == 0:
                logger.warning("LLM response is empty.")
            elif "news" not in response.lower():
                logger.warning("LLM response may be incomplete or missing news content.")
            else:
                logger.info("LLM response generated successfully.")

            return response
        except Exception as e:
            logger.error(f"Error during news generation: {e}")
            raise RuntimeError(f"Error during news generation: {e}")

if __name__ == "__main__":
    news = DAILY_NEWS()
    today = datetime.today().strftime("%Y-%m-%d")
    news_content = news.get_news()

    db_path = os.path.join(project_root, "data", "database", "daily_news.json")

    if os.path.exists(db_path):
        with open(db_path, "r", encoding="utf-8") as f:
            try:
                daily_news = json.load(f)
            except Exception:
                daily_news = {}
    else:
        daily_news = {}

    daily_news[today] = news_content

    with open(db_path, "w", encoding="utf-8") as f:
        json.dump(daily_news, f, ensure_ascii=False, indent=2)

    print(f"News for {today} saved to {db_path}")
