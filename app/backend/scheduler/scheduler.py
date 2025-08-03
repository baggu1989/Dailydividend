from gevent import monkey
monkey.patch_all()
from celery.schedules import crontab
from backend.tasks.send_message import celery_app, send_message_to_user
from news import DAILY_NEWS
import logging

celery_app.conf.timezone = 'Asia/Kolkata'
celery_app.conf.enable_utc = False

logger = logging.getLogger(__name__)

def get_all_user_ids():
    import os
    import json

    users_path = os.path.join(os.path.dirname(__file__), "users.json")
    try:
        with open(users_path, "r", encoding="utf-8") as f:
            users_data = json.load(f)
        # users_data is a list of dicts with 'number' key
        user_ids = [f"whatsapp:{user['number']}" for user in users_data if "number" in user]
        return user_ids
    except Exception as e:
        logger.error(f"Error loading user IDs: {e}")
        return []

@celery_app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    
    sender.add_periodic_task(
        crontab(hour=14, minute=25),
        send_daily_messages.s()
    )

@celery_app.task
def send_daily_messages():
    user_ids = get_all_user_ids()
    news = DAILY_NEWS()
    try:
        message = news.get_news()
        for user_id in user_ids:
            send_message_to_user.delay(user_id, message)
    except Exception as e:
        logger.error(f"Error sending daily messages: {e}")
