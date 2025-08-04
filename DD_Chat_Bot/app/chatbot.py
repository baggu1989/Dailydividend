from typing import List, Dict, TypedDict
from langchain.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from app.config import settings
from app.logging.logger import logger
from app.news_fetcher import fetch_combined_news
from langchain_groq import ChatGroq  # Adjust import if needed
from langgraph.graph import StateGraph, END
import re

class ChatState(TypedDict):
    query: str
    results: List[str]
    response: str

def retrieve_news(state: ChatState):
    """Retrieve relevant news articles for the user's query."""
    try:
        embedder = HuggingFaceEmbeddings(model_name=settings.EMBED_MODEL)
        vectorstore = Chroma(persist_directory=settings.CHROMA_PATH, embedding_function=embedder)
        retriever = vectorstore.as_retriever(search_kwargs={"k": 5})
        docs = retriever.get_relevant_documents(state["query"])
        state["results"] = [doc.page_content for doc in docs]
        logger.info(f"Retrieved {len(docs)} news articles for query: {state['query']}")
    except Exception as e:
        logger.error(f"Error retrieving news: {str(e)}")
        state["results"] = ["Unable to retrieve relevant news at this time."]
    return state

def generate_response(state: ChatState):
    """Generate a response using the retrieved news articles."""
    try:
        news_content = "\n".join(state.get("results", []))
        prompt = f"""
You are a financial news assistant. Use the following news articles to answer the user's query.

--- User Query ---
{state['query']}

--- Retrieved News ---
{news_content}

Please provide a clear, informative response using the available news information.
"""
        # Call ChatGroq with model from config
        #import pdb; pdb.set_trace()  # Debugging line, remove in production
        llm = ChatGroq(model_name=settings.LLM_MODEL)
        state["response"] = llm.invoke(prompt)
        #import pdb;pdb.set_trace()  # Debugging line, remove in production
        logger.info("Generated response for user query using ChatGroq.")
    except Exception as e:
        logger.error(f"Error generating response: {str(e)}")
        state["response"] = "I apologize, but I'm experiencing technical difficulties. Please try again in a moment."
    return state

def build_graph():
    graph = StateGraph(ChatState)
    graph.add_node("retrieve", retrieve_news)
    graph.add_node("respond", generate_response)
    graph.set_entry_point("retrieve")
    graph.add_edge("retrieve", "respond")
    graph.add_edge("respond", END)
    return graph.compile()
