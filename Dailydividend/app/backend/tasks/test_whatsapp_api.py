#!/usr/bin/env python
"""
Command-line utility for testing the WhatsApp API.
"""
import os
import sys
import logging
import argparse
import json
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# Add the parent directory to the path so we can import the modules
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

# Load environment variables
from dotenv import load_dotenv
env_path = Path(current_dir) / '.env'
load_dotenv(dotenv_path=env_path)

# Import WhatsApp client
try:
    from whatsapp_client import WhatsAppClient
    WHATSAPP_AVAILABLE = True
except ImportError as e:
    logger.error(f"Failed to import WhatsApp client: {e}")
    logger.error("Make sure the whatsapp_client.py file is in the same directory")
    WHATSAPP_AVAILABLE = False

def check_whatsapp_token():
    """Test the WhatsApp API token validity"""
    if not WHATSAPP_AVAILABLE:
        logger.error("WhatsApp client module is not available")
        return False
        
    try:
        client = WhatsAppClient()
        is_valid, details = client.check_token_validity()
        
        if is_valid:
            logger.info("✅ WhatsApp API token is valid!")
            logger.info(f"Phone number details: {details.get('data', {})}")
            return True
        else:
            logger.error("❌ WhatsApp API token is invalid or expired!")
            logger.error(f"Error details: {details}")
            logger.error("\nPlease refresh your token in the .env file")
            return False
    except Exception as e:
        logger.error(f"Error checking WhatsApp token: {str(e)}")
        return False

def send_message(number, message):
    """Send a message via the WhatsApp API"""
    if not WHATSAPP_AVAILABLE:
        logger.error("WhatsApp client module is not available")
        return False
        
    try:
        # Clean up the phone number if needed
        if number.startswith("whatsapp:"):
            number = number.replace("whatsapp:", "")
        if number.startswith("+"):
            number = number[1:]
            
        logger.info(f"Sending message to {number} via WhatsApp API...")
        client = WhatsAppClient()
        result = client.send_message(number, message)
        
        if isinstance(result, dict) and "error" in result:
            logger.error(f"Failed to send message: {result.get('error')}")
            return False
        else:
            logger.info(f"Message sent successfully!")
            return True
    except Exception as e:
        logger.error(f"Error sending message: {str(e)}")
        return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="WhatsApp API Test Utility")
    parser.add_argument("--check-token", action="store_true", help="Check if the WhatsApp API token is valid")
    parser.add_argument("--send", action="store_true", help="Send a test message")
    parser.add_argument("--number", type=str, help="Phone number to send the message to")
    parser.add_argument("--message", type=str, help="Message text to send")
    
    args = parser.parse_args()
    
    if args.check_token:
        success = check_whatsapp_token()
        sys.exit(0 if success else 1)
    
    if args.send:
        if not args.number:
            logger.error("Phone number is required for sending a message")
            sys.exit(1)
        
        message = args.message or "This is a test message from the Dailydividend WhatsApp API Test Utility."
        success = send_message(args.number, message)
        sys.exit(0 if success else 1)
    
    # If no arguments provided, show help
    if not (args.check_token or args.send):
        parser.print_help()
        sys.exit(1)
