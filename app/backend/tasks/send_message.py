from celery import Celery
import requests

celery_app = Celery("whatsapp", broker="redis://localhost:6379/0")
@celery_app.task
def send_message_to_user(number):
    pass