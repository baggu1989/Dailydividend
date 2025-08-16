import logging
from app.config import settings

logger = logging.getLogger("financial-news-bot")
logger.setLevel(getattr(settings, "LOG_LEVEL", logging.INFO))

if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        "[%(asctime)s] %(levelname)s: %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
