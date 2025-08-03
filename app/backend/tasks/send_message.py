from gevent import monkey
monkey.patch_all()
from celery import Celery
import os
import logging
import json
from datetime import datetime
from dotenv import load_dotenv
from pathlib import Path
env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)
celery_app = Celery("whatsapp", broker="redis://localhost:6379/0")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

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

@celery_app.task(bind=True, autoretry_for=(Exception,), retry_kwargs={'max_retries': 3, 'countdown': 60})
def send_message_to_user(self, number, message):
    """
    Send a WhatsApp message to the user using Twilio API with retry mechanism.
    """
    try:
        from twilio.rest import Client

        account_sid = os.getenv("TWILIO_ACCOUNT_SID")
        auth_token = os.getenv("TWILIO_AUTH_TOKEN")
        whatsapp_from = os.getenv("TWILIO_WHATSAPP_FROM") 
        
        logger.info(f"TWILIO_ACCOUNT_SID: {account_sid}")
        logger.info(f"TWILIO_AUTH_TOKEN: {auth_token}")
        logger.info(f"TWILIO_WHATSAPP_FROM: {whatsapp_from}")

        if not all([account_sid, auth_token, whatsapp_from]):
            error_msg = "Twilio credentials are not set in environment variables."
            logger.error(error_msg)
            save_failed_message(number, message, error_msg, self.request.retries)
            return

        client = Client(account_sid, auth_token)
        msg = client.messages.create(
            body=message,
            from_=whatsapp_from,
            to=number
        )
        logger.info(f"Message sent to {number}: {msg.sid}")
    except Exception as e:
        logger.error(f"Failed to send message to {number}: {str(e)} (Attempt {self.request.retries + 1})")
        
        if self.request.retries >= self.max_retries:
            save_failed_message(number, message, str(e), self.request.retries)
            logger.error(f"Max retries reached for {number}. Message details saved to failed_messages.json")
        else:
            logger.info(f"Retrying in 60 seconds... (Attempt {self.request.retries + 1}/{self.max_retries + 1})")
        
        raise e
