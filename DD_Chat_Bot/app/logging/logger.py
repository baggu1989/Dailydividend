import logging
from app.config import settings

logger = logging.getLogger("financial-news-bot")
logger.setLevel(settings.LOG_LEVEL)
handler = logging.StreamHandler()
formatter = logging.Formatter("[%(asctime)s] %(levelname)s: %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)
