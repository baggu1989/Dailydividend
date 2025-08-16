from gevent import monkey
monkey.patch_all()
from celery import Celery
import os
import sys
import logging
import json
from datetime import datetime
from dotenv import load_dotenv
from pathlib import Path

# Ensure the current directory is in the path so that local modules can be imported
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

# Load environment variables
env_path = Path(current_dir) / '.env'
if not env_path.exists():
    env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

# Initialize Celery
broker_url = os.environ.get('CELERY_BROKER_URL', 'redis://localhost:6379/0')
result_backend = os.environ.get('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')
celery_app = Celery("whatsapp", broker=broker_url, backend=result_backend)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# Import the WhatsAppClient only once at the module level
try:
    from whatsapp_client import WhatsAppClient
    logger.info("WhatsAppClient imported successfully")
    WHATSAPP_AVAILABLE = True
except ImportError as e:
    logger.error(f"WhatsAppClient import error: {e}")
    logger.error("WhatsApp API is required for sending messages")
    WHATSAPP_AVAILABLE = False

def save_failed_message(number, message, error, retry_count=0):
    """
    Save failed message details to a JSON file.
    """
    failed_message_data = {
        "number": number,
        "message": message,
        "timestamp": datetime.now().isoformat(),
        "error": str(error),
        "retry_count": retry_count
    }
    
    current_dir = Path(__file__).parent
    failed_messages_file = current_dir / "failed_messages.json"
    
    try:
        # Load existing data or create empty list
        if failed_messages_file.exists():
            with open(failed_messages_file, 'r', encoding='utf-8') as f:
                failed_messages = json.load(f)
        else:
            failed_messages = []
        
        # Add new failed message
        failed_messages.append(failed_message_data)
        
        # Save back to file
        with open(failed_messages_file, 'w', encoding='utf-8') as f:
            json.dump(failed_messages, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Failed message details saved to {failed_messages_file}")
    except Exception as e:
        logger.error(f"Failed to save failed message details: {str(e)}")

def check_whatsapp_token():
    """
    Check if the WhatsApp API token is valid.
    Prints the result to the console.
    """
    try:
        if not WHATSAPP_AVAILABLE:
            logger.error("❌ WhatsApp client module is not available")
            return False, {"error": "WhatsApp client module not available"}
            
        client = WhatsAppClient()
        is_valid, details = client.check_token_validity()
        
        if is_valid:
            logger.info("✅ WhatsApp API token is valid!")
            logger.info(f"Phone number details: {json.dumps(details['data'], indent=2)}")
        else:
            logger.error("❌ WhatsApp API token is invalid or expired!")
            logger.error(f"Error details: {json.dumps(details, indent=2)}")
            logger.error("\nPlease refresh your token in the .env file")
        
        return is_valid, details
    except Exception as e:
        logger.error(f"Error checking WhatsApp token: {str(e)}")
        return False, {"error": str(e)}

@celery_app.task(bind=True, autoretry_for=(Exception,), retry_kwargs={'max_retries': 3, 'countdown': 60})
def send_message_to_user(self, number, message):
    """
    Send a WhatsApp message to the user using WhatsApp Business API with retry mechanism.
    """
    try:
        # Check if WhatsApp API is available
        if not WHATSAPP_AVAILABLE:
            error_msg = "WhatsApp API module is not available. Cannot send messages."
            logger.error(error_msg)
            save_failed_message(number, message, error_msg, self.request.retries)
            raise ImportError(error_msg)
        
        # Check for required environment variables
        whatsapp_api_token = os.getenv("WHATSAPP_API_TOKEN")
        whatsapp_phone_id = os.getenv("WHATSAPP_PHONE_NUMBER_ID")
        
        if not whatsapp_api_token or not whatsapp_phone_id:
            error_msg = "WhatsApp API credentials are not set in environment variables."
            logger.error(error_msg)
            save_failed_message(number, message, error_msg, self.request.retries)
            raise ValueError(error_msg)
            
        # Send message via WhatsApp Business API
        logger.info(f"Sending message to {number} via WhatsApp Business API")
        
        # Clean up the phone number if needed
        if number.startswith("whatsapp:"):
            number = number.replace("whatsapp:", "")
        if number.startswith("+"):
            number = number[1:]
            
        client = WhatsAppClient()
        result = client.send_message(number, message)
        
        if isinstance(result, dict) and "error" in result:
            error_msg = f"WhatsApp Business API send failed: {result.get('error')}"
            logger.error(error_msg)
            
            if self.request.retries >= self.max_retries:
                save_failed_message(number, message, error_msg, self.request.retries)
                logger.error(f"Max retries reached for {number}. Message details saved to failed_messages.json")
            else:
                logger.info(f"Retrying in 60 seconds... (Attempt {self.request.retries + 1}/{self.max_retries + 1})")
                
            raise Exception(error_msg)
        else:
            logger.info(f"Message sent successfully to {number} via WhatsApp Business API")
            
    except Exception as e:
        if not isinstance(e, (ImportError, ValueError)):  # Don't retry on configuration errors
            logger.error(f"Failed to send message to {number}: {str(e)} (Attempt {self.request.retries + 1})")
            
            if self.request.retries >= self.max_retries:
                save_failed_message(number, message, str(e), self.request.retries)
                logger.error(f"Max retries reached for {number}. Message details saved to failed_messages.json")
            else:
                logger.info(f"Retrying in 60 seconds... (Attempt {self.request.retries + 1}/{self.max_retries + 1})")
            
        raise e

# Command line interface for testing
if __name__ == "__main__":
    import sys
    import argparse
    
    parser = argparse.ArgumentParser(description="WhatsApp Message Sender")
    parser.add_argument("--test", action="store_true", help="Test the WhatsApp token validity")
    parser.add_argument("--send", action="store_true", help="Send a test message")
    parser.add_argument("--number", type=str, help="Phone number to send the message to")
    parser.add_argument("--message", type=str, help="Message text to send")
    
    args = parser.parse_args()
    
    if args.test:
        is_valid, details = check_whatsapp_token()
        sys.exit(0 if is_valid else 1)
    
    # Always send a message to +918700725940 if this file is run directly
    # (unless we're just testing token validity)
    if not args.test:
        target_number = "918700725940"  # Removing + as the client handles formatting
        message = "This is an automated message from Dailydividend WhatsApp sender."
        
        logger.info(f"Automatically sending message to {target_number}")
        try:
            if not WHATSAPP_AVAILABLE:
                logger.error("WhatsApp client module is not available")
                sys.exit(1)
                
            client = WhatsAppClient()
            result = client.send_message(target_number, message)
            
            if isinstance(result, dict) and "error" in result:
                logger.error(f"Failed to send message to {target_number}: {result.get('error')}")
            else:
                logger.info(f"Message sent successfully to {target_number}")
        except Exception as e:
            logger.error(f"Error sending message to {target_number}: {str(e)}")
    
    # Process command line arguments for sending messages
    if args.send:
        if not args.number:
            logger.error("Phone number is required for sending a message")
            sys.exit(1)
        
        message = args.message or "This is a test message from the Dailydividend WhatsApp sender."
        
        try:
            if not WHATSAPP_AVAILABLE:
                logger.error("WhatsApp client module is not available")
                sys.exit(1)
                
            client = WhatsAppClient()
            result = client.send_message(args.number, message)
            
            if isinstance(result, dict) and "error" in result:
                logger.error(f"Failed to send message via WhatsApp API: {result.get('error')}")
                sys.exit(1)
            else:
                logger.info(f"Message sent successfully via WhatsApp API")
                sys.exit(0)
        except Exception as e:
            logger.error(f"Error sending message via WhatsApp API: {str(e)}")
            sys.exit(1)
