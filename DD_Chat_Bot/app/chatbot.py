from typing import List, Dict, TypedDict
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from app.config import settings
from app.logging.logger import logger
from app.news_fetcher import fetch_combined_news
from langchain_groq import ChatGroq  
from langgraph.graph import StateGraph, END
import re
#from app.news_fetcher import fetch_news_from_duckduckgo
from openai import OpenAI
class ChatState(TypedDict):
    query: str
    results: List[str]
    response: str
    memory: List[Dict[str, str]]  
    not_related: bool
    usage: Dict[str, int]



def retrieve_news(state: ChatState):
    """Retrieve relevant news articles for the user's query."""
    try:
        # embedder = HuggingFaceEmbeddings(model_name=settings.EMBED_MODEL)
        # vectorstore = Chroma(persist_directory=settings.CHROMA_PATH, embedding_function=embedder)
        # retriever = vectorstore.as_retriever(search_kwargs={"k": 5})
        # docs = retriever.get_relevant_documents(state["query"])
        # #import pdb; pdb.set_trace()  # Debugging line, remove in production
        # state["results"] = [doc.page_content for doc in docs]
        # logger.info(f"Retrieved {len(docs)} news articles for query: {state['query']}")
        # docs=[]
        # if len(docs) == 0:
        #     news="" #fetch_news_from_duckduckgo(state["query"])
        #     if not news:
        #         state["results"] = ["No relevant news articles found."]
        #     else:
        #         state["results"] = [news_item["article_content"]+news_item['news_content'] for news_item in news ]
        #         import json
        #         #json_string = json.dumps(news)
        #         #state["results"] =[news ]
        #         logger.info(f"Fetched {len(state['results'])} articles from DuckDuckGo for query: {state['query']}")
        state["results"] =["No news fetchinng is required" ]


    except Exception as e:
        logger.error(f"Error retrieving news: {str(e)}")
        state["results"] = ["Unable to retrieve relevant news at this time."]
    return state

def generate_response(state: ChatState):
    """Generate a response using the retrieved news articles and conversation history."""
    try:
        # Build conversation history string
        if  state.get("not_related"):
            return state 
        else:
            history = ""
            # for turn in state.get("memory", []):
            #     history += f"User: {turn['user']}\nBot: {turn['bot']}\n"
            # news_content = "\n".join(state.get("results", []))
            news_content=""
            prompt = f"""
    You are only financial informant and reject if request is not related . Respond to queries with the following checklist 

All market data must be extremely current and accurate
Make sure to use % changes and number, facts and figures were relevant
Make sure it is a Mobile-friendly chat format under 200 words. Use bold Headlines and text in bullet points where possible
Always verify the sources
Always mention at the end after a line space “Disclaimer: Educational Purposes only“


Do not provide investment advice - if asked for your opinion on whether to buy or sell any financial instruments mention 

“I cannot provide investment advice, but I can provide information” and then provide any relevant information from the web with sources 
 
    --- User Query ---
    {state['query']}

    """
            
            llm =  ChatGroq(model_name=settings.LLM_MODEL)
            response_obj = llm.invoke(prompt)
            response_str = response_obj.content if hasattr(response_obj, "content") else str(response_obj)
            logger.info(f"Response LLM raw output: {response_str.strip()}")
            state["response"] = response_str.strip()
            
            state["usage"] = {
                "prompt_tokens": response_obj.usage_metadata['input_tokens'],
                "completion_tokens": response_obj.usage_metadata['output_tokens'], 
                "total_tokens": response_obj.usage_metadata['total_tokens']
            }
            logger.info("Generated response for user query using ChatGroq.")
           
            return state
    except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            state["response"] = "I apologize, but I'm experiencing technical difficulties. Please try again in a moment."
            

def build_graph():
    graph = StateGraph(ChatState)
   
    graph.add_node("retrieve", retrieve_news)
    graph.add_node("respond", generate_response)
    graph.set_entry_point("retrieve")
    
    graph.add_edge("respond", END)
    return graph.compile()
