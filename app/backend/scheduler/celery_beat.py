import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from backend.tasks.send_message import celery_app
# Import the scheduler module to register the periodic tasks defined within it.
from backend.scheduler import scheduler

celery_app.start(["beat", "--loglevel=info"])
