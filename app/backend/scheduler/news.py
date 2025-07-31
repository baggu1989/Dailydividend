import sys
import os
import requests


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

class DAILY_NEWS:
    def __init__(self):
        try:
            groq_instance = Groq()          
            self.llm = groq_instance.get_llm()  
        except Exception as e:
            raise RuntimeError(f"Failed to initialize LLM: {e}")
        self.prompt = DAILY_PROMPT
        self.news = News()
    def combine_news(self,news_list):
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
        sp500_change = get_index_change("^GSPC")
        eurostoxx_change = get_index_change("^STOXX50E")
        ftse100_change = get_index_change("^FTSE")
        news = self.combine_news((self.news.fetch_marketaux_news() +self.news.fetch_yahoo_financial_headlines())[:10])


        if not self.llm:
            raise RuntimeError("LLM is not initialized.")
        
        try:
            prompt = ChatPromptTemplate.from_messages([
                ('system', self.prompt),('human',"here are the top financial news : \n"+ news )
            ])
            chain = prompt | self.llm | StrOutputParser()
            response = chain.invoke({
                'Day': day,
                'Month': month,
                'Date': date,
                'S&P_change':str(sp500_change),
                'Eurostoxx_change':str(eurostoxx_change),
                'FTSE_change':str(ftse100_change),
                
            })
            return response
        except Exception as e:
            raise RuntimeError(f"Error during news generation: {e}")


if __name__ == "__main__":
    news= DAILY_NEWS()
    print(news.get_news())
