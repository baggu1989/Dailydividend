from typing import List, Dict, TypedDict
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from app.config import settings
from app.logging.logger import logger
from app.news_fetcher import fetch_combined_news
from langchain_groq import ChatGroq  
from langgraph.graph import StateGraph, END
import re

class ChatState(TypedDict):
    query: str
    results: List[str]
    response: str
    memory: List[Dict[str, str]]  
    not_related: bool

def check_finance_related_node(state: ChatState):
    """
    Node to check if the user's query is related to finance, market, or economy.
    If not related, set a response and skip further processing.
    """
    prompt = f"""
You are an expert financial assistant. 
Determine if the following user query is related to finance, stock market, or the economy.
If it is not related, respond with: "Your query is not related to finance, market, or economy."
If it is related, respond with: "Related".

User Query:
{state['query']}
"""
    llm = ChatGroq(model_name=settings.LLM_MODEL)
    response_obj = llm.invoke(prompt)
    response_str = response_obj.content if hasattr(response_obj, "content") else str(response_obj)
    logger.info(f"Guardrail LLM raw response: {response_str.strip()}")
    # Make the check more robust
    resp_lower = response_str.strip().lower()
    if "not related" in resp_lower or "your query is not related to finance" in resp_lower:
        state["response"] = "Your query is not related to finance, market, or economy."
        state["results"] = []
        state["not_related"] = True
    else:
        state["not_related"] = False
    logger.info(f"Guardrail check result: {resp_lower}")
    return state

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
    """Generate a response using the retrieved news articles and conversation history."""
    try:
        # Build conversation history string
        if  state.get("not_related"):
            return state 
        else:
            history = ""
            for turn in state.get("memory", []):
                history += f"User: {turn['user']}\nBot: {turn['bot']}\n"
            news_content = "\n".join(state.get("results", []))
            prompt = f"""
    You are a financial news assistant. Here is the conversation so far:
    {history}

    --- User Query ---
    {state['query']}

    --- Retrieved News ---
    {news_content}

    Please provide a clear, informative response using the available news information and conversation history. if no information is avaiable , you can act as financial educator and answer the query based on your knowledge.
    """
            #import pdb; pdb.set_trace()  # Debugging line, remove in production
            llm = ChatGroq(model_name=settings.LLM_MODEL)
            response_obj = llm.invoke(prompt)
            # Ensure response is a string
            response_str = response_obj.content if hasattr(response_obj, "content") else str(response_obj)
            state["response"] = response_str
            logger.info("Generated response for user query using ChatGroq.")
            import pdb; pdb.set_trace()  # Debugging line, remove in production
            return state
    except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            state["response"] = "I apologize, but I'm experiencing technical difficulties. Please try again in a moment."
            

def build_graph():
    graph = StateGraph(ChatState)
    graph.add_node("guardrail", check_finance_related_node)
    graph.add_node("retrieve", retrieve_news)
    graph.add_node("respond", generate_response)
    graph.set_entry_point("guardrail")
    # If related, continue to retrieve news; if not, go directly to respond
    import pdb; pdb.set_trace()  # Debugging line, remove in production
    graph.add_conditional_edges(
        "guardrail",
        lambda state: ["respond"] if state.get("not_related") else ["retrieve"]
    )
    graph.add_edge("retrieve", "respond")
    graph.add_edge("respond", END)
    return graph.compile()
