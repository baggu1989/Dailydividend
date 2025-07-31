from celery.schedules import crontab
from tasks.send_message import celery_app, send_message_to_user

def get_all_user_ids():
    # return the list of all the number from the database
    pass

@celery_app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    # Every day at 8:00 AM
    sender.add_periodic_task(
        crontab(hour=8, minute=0),
        send_daily_messages.s()
    )

@celery_app.task
def send_daily_messages():
    user_ids = get_all_user_ids()
    for user_id in user_ids:
        send_message_to_user.delay(user_id)
