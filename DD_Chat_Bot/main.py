from fastapi import FastAPI, HTTPException, Form, Request, Response, Header, Depends
from fastapi.responses import PlainTextResponse
from typing import Dict, List, Optional
import json
import os
from dotenv import load_dotenv
from pathlib import Path

# Explicitly load environment variables from the .env file
env_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path)

from app.chatbot import build_graph, generate_response
from app.config import settings
from app.logging.logger import logger
from app.whatsapp_client import WhatsAppClient
from schema.chat_models import ChatResponse
from schema.models import HealthStatus

app = FastAPI(title="Financial News Chatbot", description="AI-powered chatbot for financial news and market analysis")
user_sessions: Dict[str, List[Dict[str, str]]] = {}
chatbot = build_graph()

# WhatsApp Meta API client
whatsapp_client = WhatsAppClient()

@app.get("/webhook")
async def verify_webhook(request: Request):
    """
    Endpoint for WhatsApp webhook verification
    
    WhatsApp requires verification of the webhook URL by returning the challenge code
    that is sent as a query parameter
    """
    # Parse query parameters
    query_params = dict(request.query_params)
    
    # Extract verification parameters
    mode = query_params.get("hub.mode")
    token = query_params.get("hub.verify_token")
    challenge = query_params.get("hub.challenge")
    
    # Debug the tokens
    expected_token = os.getenv("WHATSAPP_VERIFY_TOKEN", "")
    logger.info(f"Webhook verification: mode={mode}, token={token}, challenge={challenge}")
    logger.info(f"Expected token: '{expected_token}', received token: '{token}'")
    
    # Hard-code the token for testing (remove in production)
    hardcoded_token = "rohan"
    
    # Verify the mode and token with multiple checks
    if mode == "subscribe" and (token == expected_token or token == hardcoded_token):
        logger.info("Webhook verified successfully")
        return PlainTextResponse(content=challenge)
    else:
        logger.error(f"Webhook verification failed. Token mismatch or invalid mode.")
        return Response(status_code=403)

@app.post("/webhook")
async def webhook(request: Request):
    """
    Webhook endpoint for receiving WhatsApp messages from Meta API
    """
    try:
        # Parse the request body
        body = await request.json()
        logger.info(f"Received webhook: {json.dumps(body, indent=2)}")
        
        # Check if this is a valid WhatsApp message
        if "object" in body and body["object"] == "whatsapp_business_account":
            processed = False
            # Process each entry
            for entry in body.get("entry", []):
                # Process each change
                for change in entry.get("changes", []):
                    if change.get("field") == "messages":
                        value = change.get("value", {})
                        # Process each message
                        for message in value.get("messages", []):
                            if message.get("type") == "text":
                                # Extract message information
                                phone_number = message.get("from", "")
                                message_body = message.get("text", {}).get("body", "")
                                message_id = message.get("id", "")
                                
                                # Process the message and generate response
                                await process_message(phone_number, message_body, message_id)
                                processed = True
            
            if processed:                
                # Return a 200 OK to acknowledge receipt
                return {"status": "success"}
            else:
                logger.warning("No text messages to process in the webhook")
                return {"status": "no_messages"}
        else:
            logger.warning(f"Received non-WhatsApp webhook: {body}")
            return {"status": "ignored"}
            
    except Exception as e:
        logger.error(f"Error processing webhook: {str(e)}")
        return {"status": "error", "message": str(e)}

@app.post("/chat", response_model=ChatResponse)
async def chat(
    From: str = Form(...),  # Sender's WhatsApp number
    Body: str = Form(...)   # Message content
):
    """
    Legacy chat endpoint to handle direct API requests.
    """
    try:
        if not Body.strip():
            raise HTTPException(status_code=400, detail="Query cannot be empty")
        
        # Use the sender's WhatsApp number as the user_id
        user_id = From.replace("whatsapp:", "")
        response_str = await process_and_generate_response(user_id, Body)
        
        return ChatResponse(
            response=response_str,
            topic="general",
            confidence=None,
            user_id=user_id
        )
    except Exception as e:
        logger.error(f"Error processing chat request: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Store processed message IDs to avoid duplicates
processed_messages = set()

async def process_message(phone_number: str, message_text: str, message_id: str):
    """
    Process an incoming WhatsApp message and send a response
    """
    try:
        # Skip if message is empty
        if not message_text.strip():
            logger.warning(f"Received empty message from {phone_number}")
            return
            
        # Skip if we've already processed this message
        if message_id in processed_messages:
            logger.info(f"Skipping already processed message: {message_id}")
            return
        
        # Add to processed messages set
        processed_messages.add(message_id)
        logger.info(f"Processing message from {phone_number}: {message_text} (ID: {message_id})")
        
        # Generate response
        response_text = await process_and_generate_response(phone_number, message_text)
        
        # Send response via WhatsApp API
        result = whatsapp_client.send_message(phone_number, response_text)
        
        if isinstance(result, dict) and "error" in result:
            logger.error(f"Error sending message: {result['error']}")
        else:
            logger.info(f"Message sent successfully: {result}")
        
    except Exception as e:
        logger.error(f"Error processing message: {str(e)}")

async def process_and_generate_response(user_id: str, query: str) -> str:
    """
    Process a user query and generate a response using the LLM
    """
    memory = user_sessions.get(user_id, [])
    state = {
        "query": query,
        "memory": memory
    }
    
    logger.info(f"Generating response for query from {user_id}: {query}")
    
    # Retrieve news and generate response using LLM
    state = chatbot.invoke(state)
    state = generate_response(state)  # Explicitly call LLM
    
    # Append the current query and response to the memory
    memory.append({"user": query, "bot": state["response"]})
    user_sessions[user_id] = memory  # Update the user's session
    
    # Ensure response is a string
    response_obj = state.get("response")
    if hasattr(response_obj, "content"):
        response_str = response_obj.content
    elif isinstance(response_obj, str):
        response_str = response_obj
    else:
        response_str = "No response generated."
        
    return response_str

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
            "webhook": "/webhook",
            "chat": "/chat",
            "health": "/health",
            "debug": "/debug",
            "check-token": "/check-token"
        }
    }

@app.get("/debug")
def debug():
    """
    Debug endpoint to check environment variables
    """
    return {
        "WHATSAPP_VERIFY_TOKEN": settings.WHATSAPP_VERIFY_TOKEN,
        "WHATSAPP_VERIFY_TOKEN_LENGTH": len(settings.WHATSAPP_VERIFY_TOKEN) if settings.WHATSAPP_VERIFY_TOKEN else 0,
        "WHATSAPP_API_TOKEN_SET": bool(settings.WHATSAPP_API_TOKEN),
        "WHATSAPP_PHONE_NUMBER_ID_SET": bool(settings.WHATSAPP_PHONE_NUMBER_ID),
        "WHATSAPP_BUSINESS_ACCOUNT_ID_SET": bool(settings.WHATSAPP_BUSINESS_ACCOUNT_ID)
    }

@app.get("/check-token")
def check_token():
    """
    Check if the WhatsApp API token is valid
    """
    from app.utils.token_checker import check_whatsapp_token
    
    is_valid, details = check_whatsapp_token()
    
    response = {
        "token_valid": is_valid,
        "details": details
    }
    
    if not is_valid:
        response["instructions"] = "Please refresh your token by following the instructions in docs/whatsapp_token_refresh.md"
    
    return response

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)