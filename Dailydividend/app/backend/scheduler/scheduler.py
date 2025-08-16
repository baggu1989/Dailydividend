from gevent import monkey
monkey.patch_all()
import os
import sys
from celery.schedules import crontab
from backend.tasks.send_message import celery_app, send_message_to_user
import logging
from datetime import timedelta

# Import the DAILY_NEWS class
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)
from news import DAILY_NEWS

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
        user_data = [
            {"id": f"whatsapp:{user['number']}", "frequency": user.get("frequency", 1)}
            for user in users_data if "number" in user
        ]
        return user_data
    except Exception as e:
        logger.error(f"Error loading user IDs: {e}")
        return []

@celery_app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    user_data = get_all_user_ids()
    for user in user_data:
        try:
            frequency = int(user["frequency"])  # Convert frequency to an integer
        except ValueError:
            logger.error(f"Invalid frequency value for user {user['id']}: {user['frequency']}")
            continue

        if frequency == 3:
            times = [(8, 0), (12, 0), (23, 59)]  # 8:00 AM, 12:00 PM, 11:59 PM
        elif frequency == 2:
            times = [(12, 0), (23, 59)]  # 12:00 PM, 12:00 AM
        else:  # Default to 1 time
            times = [(12, 0)]  # 12:00 PM (noon)

        for hour, minute in times:
            sender.add_periodic_task(
                crontab(hour=hour, minute=minute),
                send_daily_messages.s(user["id"]),
                name=f"send_message_{user['id']}_at_{hour:02d}:{minute:02d}"
            )
            logger.info(f"Scheduling task for user {user['id']} at {hour:02d}:{minute:02d}")

@celery_app.task
def send_daily_messages(user_id=None):
    user_data = get_all_user_ids()
    if user_id:
        user_data = [user for user in user_data if user["id"] == user_id]

    news = DAILY_NEWS()
    try:
        message = news.get_news()
        for user in user_data:
            send_message_to_user.delay(user["id"], message)
    except Exception as e:
        logger.error(f"Error sending daily messages: {e}")
