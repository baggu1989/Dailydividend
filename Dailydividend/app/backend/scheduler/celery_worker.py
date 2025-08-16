import sys
import os

# Add app directory to path
app_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, app_dir)

# Add tasks directory to path to ensure modules can be imported
tasks_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'tasks'))
if tasks_dir not in sys.path:
    sys.path.insert(0, tasks_dir)

# Import required modules
from backend.tasks.send_message import celery_app
from backend.scheduler import scheduler

# Start the Celery worker
celery_app.worker_main(["worker", "--loglevel=info", "--pool=gevent"])
