import logging
from logging.handlers import TimedRotatingFileHandler
from app.config import settings
import os

# Define log directory
LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)  # Create folder if not exists

# File path for logs
LOG_FILE = os.path.join(LOG_DIR, "financial-news-bot.log")


logger = logging.getLogger("financial-news-bot")
logger.setLevel(settings.LOG_LEVEL)
# Console handler (optional, keep logs in terminal too)
console_handler = logging.StreamHandler()
console_formatter = logging.Formatter("[%(asctime)s] %(levelname)s: %(message)s")
console_handler.setFormatter(console_formatter)
logger.addHandler(console_handler)

# File handler with daily rotation
file_handler = TimedRotatingFileHandler(
    LOG_FILE, when="midnight", interval=1, backupCount=7, encoding="utf-8"
)
file_formatter = logging.Formatter("[%(asctime)s] %(levelname)s: %(message)s")
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)
