import requests
import json
from app.config import settings
from app.logging.logger import logger

import os
from dotenv import load_dotenv
from pathlib import Path

# Explicitly load environment variables
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

class WhatsAppClient:
    def __init__(self):
        # Get values directly from environment variables
        self.api_token = os.getenv("WHATSAPP_API_TOKEN", "")
        self.phone_number_id = os.getenv("WHATSAPP_PHONE_NUMBER_ID", "")
        
        # Log the configuration
        logger.info(f"WhatsApp Client initialized with phone_number_id: {self.phone_number_id}")
        logger.info(f"API token length: {len(self.api_token)}")
        
        # Updated API endpoint - this is the correct format for the WhatsApp Cloud API
        self.base_url = f"https://graph.facebook.com/v19.0/{self.phone_number_id}/messages"
        self.headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json"
        }

    def send_message(self, recipient_phone_number, message_text):
        """
        Send a message using the WhatsApp Cloud API
        
        Args:
            recipient_phone_number (str): The recipient's phone number in international format without the "+" sign
            message_text (str): The message text to send
            
        Returns:
            dict: The API response
        """
        try:
            # Debug information
            logger.info(f"Sending message to {recipient_phone_number} using API URL: {self.base_url}")
            logger.info(f"Authorization header: Bearer {self.api_token[:10]}...")
            
            # Ensure proper formatting of the payload
            payload = {
                "messaging_product": "whatsapp",
                "recipient_type": "individual",
                "to": recipient_phone_number,
                "type": "text",
                "text": {
                    "preview_url": False,
                    "body": message_text
                }
            }
            
            # Debug payload
            logger.info(f"Sending payload: {json.dumps(payload, indent=2)}")
            
            response = requests.post(
                self.base_url,
                headers=self.headers,
                json=payload  # Using json parameter instead of data with json.dumps
            )
            
            if response.status_code == 200:
                logger.info(f"Message sent successfully to {recipient_phone_number}")
                return response.json()
            elif response.status_code == 401:
                error_data = response.json().get("error", {})
                error_code = error_data.get("code")
                error_subcode = error_data.get("error_subcode")
                
                if error_code == 190:  # Authentication error
                    logger.error("WhatsApp API TOKEN HAS EXPIRED! Please generate a new token in Meta Developer Dashboard")
                    logger.error("Visit https://developers.facebook.com/apps/ to generate a new token")
                    logger.error(f"Error details: {response.text}")
                    return {"error": "API token expired. Please generate a new token.", "details": response.text}
                else:
                    logger.error(f"Authentication failed: {response.status_code} - {response.text}")
                    return {"error": response.text}
            else:
                logger.error(f"Failed to send message: {response.status_code} - {response.text}")
                return {"error": response.text}
                
        except Exception as e:
            logger.error(f"Error sending WhatsApp message: {str(e)}")
            return {"error": str(e)}
