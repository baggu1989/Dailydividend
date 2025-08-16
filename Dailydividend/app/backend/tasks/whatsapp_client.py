import requests
import json
import os
import logging
from pathlib import Path
from dotenv import load_dotenv

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# Load environment variables
env_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path)

class WhatsAppClient:
    """
    Client for sending messages using the WhatsApp Cloud API.
    """
    def __init__(self):
        """Initialize the WhatsApp client with credentials from environment variables."""
        self.api_token = os.getenv("WHATSAPP_API_TOKEN", "")
        self.phone_number_id = os.getenv("WHATSAPP_PHONE_NUMBER_ID", "")
        
        if not self.api_token or not self.phone_number_id:
            logger.warning("WhatsApp API token or phone number ID not found in environment variables")
        else:
            logger.info(f"WhatsApp client initialized with phone_number_id: {self.phone_number_id}")
            logger.info(f"API token length: {len(self.api_token)}")
        
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
            # Remove any "whatsapp:" prefix if present
            if recipient_phone_number.startswith("whatsapp:"):
                recipient_phone_number = recipient_phone_number.replace("whatsapp:", "")
                
            # Remove "+" if present at the beginning of the phone number
            if recipient_phone_number.startswith("+"):
                recipient_phone_number = recipient_phone_number[1:]
                
            logger.info(f"Sending message to {recipient_phone_number} using WhatsApp API")
            
            # Format the payload according to WhatsApp Cloud API requirements
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
            
            # Send the request
            response = requests.post(
                self.base_url,
                headers=self.headers,
                json=payload
            )
            
            if response.status_code == 200:
                logger.info(f"Message sent successfully to {recipient_phone_number}")
                return response.json()
            elif response.status_code == 401:
                error_data = response.json().get("error", {})
                error_code = error_data.get("code")
                
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

    def send_template_message(self, recipient_phone_number, template_name, components=None, language_code="en_US"):
        """
        Send a template message using the WhatsApp Cloud API
        
        Args:
            recipient_phone_number (str): The recipient's phone number in international format without the "+" sign
            template_name (str): The name of the pre-approved template
            components (list, optional): Template components like header, body parameters, etc.
            language_code (str): Language code for the template, default is "en_US"
            
        Returns:
            dict: The API response
        """
        try:
            # Clean up the phone number
            if recipient_phone_number.startswith("whatsapp:"):
                recipient_phone_number = recipient_phone_number.replace("whatsapp:", "")
                
            if recipient_phone_number.startswith("+"):
                recipient_phone_number = recipient_phone_number[1:]
                
            logger.info(f"Sending template message '{template_name}' to {recipient_phone_number} using WhatsApp API")
            
            # Build the template payload
            payload = {
                "messaging_product": "whatsapp",
                "recipient_type": "individual",
                "to": recipient_phone_number,
                "type": "template",
                "template": {
                    "name": template_name,
                    "language": {
                        "code": language_code
                    }
                }
            }
            
            # Add components if provided
            if components:
                payload["template"]["components"] = components
                
            # Send the request
            response = requests.post(
                self.base_url,
                headers=self.headers,
                json=payload
            )
            
            if response.status_code == 200:
                logger.info(f"Template message sent successfully to {recipient_phone_number}")
                return response.json()
            elif response.status_code == 401:
                error_data = response.json().get("error", {})
                error_code = error_data.get("code")
                
                if error_code == 190:  # Authentication error
                    logger.error("WhatsApp API TOKEN HAS EXPIRED! Please generate a new token in Meta Developer Dashboard")
                    logger.error("Visit https://developers.facebook.com/apps/ to generate a new token")
                    logger.error(f"Error details: {response.text}")
                    return {"error": "API token expired. Please generate a new token.", "details": response.text}
                else:
                    logger.error(f"Authentication failed: {response.status_code} - {response.text}")
                    return {"error": response.text}
            else:
                logger.error(f"Failed to send template message: {response.status_code} - {response.text}")
                return {"error": response.text}
                
        except Exception as e:
            logger.error(f"Error sending WhatsApp template message: {str(e)}")
            return {"error": str(e)}
            
    def check_token_validity(self):
        """
        Check if the WhatsApp API token is valid.
        
        Returns:
            tuple: (is_valid, details) where is_valid is a boolean and details is a dict with additional info
        """
        if not self.api_token or not self.phone_number_id:
            return False, {"error": "Missing API token or phone number ID in environment variables"}
        
        # Construct URL for a simple GET request to check the token
        url = f"https://graph.facebook.com/v19.0/{self.phone_number_id}"
        
        try:
            response = requests.get(url, headers=self.headers)
            
            if response.status_code == 200:
                return True, {"message": "Token is valid", "data": response.json()}
            else:
                error_data = response.json().get("error", {})
                if error_data.get("code") == 190:
                    return False, {"error": "API token has expired", "details": error_data}
                return False, {"error": f"API request failed with status {response.status_code}", "details": error_data}
        
        except Exception as e:
            return False, {"error": f"Exception occurred: {str(e)}"}
