from fastapi import FastAPI, HTTPException, Query
from typing import Dict, List, Optional
from langgraph.graph import StateGraph, END
from app.chatbot import build_graph, generate_response  # Import generate_response
from app.config import settings
from app.logging.logger import logger
from app.marketaux_client import marketaux_client
from schema.chat_models import ChatInput, ChatResponse
from schema.models import HealthStatus

app = FastAPI(title="Financial News Chatbot", description="AI-powered chatbot for financial news and market analysis")
user_sessions: Dict[str, List[Dict[str, str]]] = {}
chatbot = build_graph()

@app.post("/chat", response_model=ChatResponse)
def chat(payload: ChatInput):
    try:
        if not payload.query or not payload.query.strip():
            raise HTTPException(status_code=400, detail="Query cannot be empty")
        
        memory = user_sessions.get(payload.user_id, [])
        state = {
            "query": payload.query,
            "memory": memory
        }
        
        logger.info(f"Received query from {payload.user_id}: {payload.query}")
        # Retrieve news and generate response using LLM
        state = chatbot.invoke(state)
        state = generate_response(state)  # Explicitly call LLM
        #import pdb; pdb.set_trace()  # Debugging line, remove in production
        # Update memory with the latest exchange
        state["memory"].append({"user": payload.query, "bot": state["response"]})
        user_sessions[payload.user_id] = state["memory"]
        
        # Ensure response is a string
        response_obj = state.get("response")
        if hasattr(response_obj, "content"):
            response_str = response_obj.content
        elif isinstance(response_obj, str):
            response_str = response_obj
        else:
            response_str = "No response generated."

        return ChatResponse(
            response=response_str,
            topic=state.get("topic", "general"),
            confidence=None,
            user_id=payload.user_id
        )
    except Exception as e:
        logger.error(f"Error processing chat request: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/health", response_model=HealthStatus)
def health_check():
    return HealthStatus(
        status="healthy",
        service="Financial News Chatbot",
        version="1.0.0"
    )

@app.get("/")
def root():
    return {
        "message": "Financial News Chatbot API",
        "endpoints": {
            "chat": "/chat",
            "health": "/health"
           
        }
    }

