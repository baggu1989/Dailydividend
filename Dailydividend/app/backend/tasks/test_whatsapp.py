#!/usr/bin/env python
"""
Command-line utility for sending WhatsApp messages directly.
This script can be run directly from the command line to test message sending
without dealing with import issues.
"""
import os
import sys
import logging
import argparse
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
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

# Load environment variables
from dotenv import load_dotenv
env_path = Path(current_dir) / '.env'
load_dotenv(dotenv_path=env_path)

def test_whatsapp_token():
    """Test the WhatsApp API token validity"""
    try:
        from tasks.whatsapp_client import WhatsAppClient
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

def send_test_message(number, message, service="whatsapp"):
    """Send a test message via the specified service"""
    if service.lower() == "whatsapp":
        try:
            from tasks.whatsapp_client import WhatsAppClient
            client = WhatsAppClient()
            logger.info(f"Sending message to {number} via WhatsApp API...")
            result = client.send_message(number, message)
            
            if isinstance(result, dict) and "error" in result:
                logger.error(f"Failed to send message via WhatsApp API: {result.get('error')}")
                return False
            else:
                logger.info(f"Message sent successfully via WhatsApp API")
                return True
        except Exception as e:
            logger.error(f"Error sending message via WhatsApp API: {str(e)}")
            return False
    else:
        try:
            from twilio.rest import Client
            account_sid = os.getenv("TWILIO_ACCOUNT_SID")
            auth_token = os.getenv("TWILIO_AUTH_TOKEN")
            whatsapp_from = os.getenv("TWILIO_WHATSAPP_FROM")
            
            if not all([account_sid, auth_token, whatsapp_from]):
                logger.error("Twilio credentials are not set in environment variables.")
                return False
            
            client = Client(account_sid, auth_token)
            msg = client.messages.create(
                body=message,
                from_=whatsapp_from,
                to=number
            )
            logger.info(f"Message sent successfully via Twilio: {msg.sid}")
            return True
        except Exception as e:
            logger.error(f"Error sending message via Twilio: {str(e)}")
            return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="WhatsApp Message Sender Utility")
    parser.add_argument("--test", action="store_true", help="Test the WhatsApp token validity")
    parser.add_argument("--send", action="store_true", help="Send a test message")
    parser.add_argument("--number", type=str, help="Phone number to send the message to")
    parser.add_argument("--message", type=str, help="Message text to send")
    parser.add_argument("--service", type=str, choices=["whatsapp", "twilio"], default="whatsapp",
                        help="Service to use for sending the message")
    
    args = parser.parse_args()
    
    if args.test:
        success = test_whatsapp_token()
        sys.exit(0 if success else 1)
    
    if args.send:
        if not args.number:
            logger.error("Phone number is required for sending a message")
            sys.exit(1)
        
        message = args.message or "This is a test message from the Dailydividend WhatsApp sender."
        success = send_test_message(args.number, message, args.service)
        sys.exit(0 if success else 1)
    
    # If no arguments provided, show help
    if not (args.test or args.send):
        parser.print_help()
        sys.exit(1)
