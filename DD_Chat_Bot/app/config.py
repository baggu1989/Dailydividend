import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    CHROMA_PATH = "/mnt/chroma-data"
    LOG_LEVEL = "INFO"
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
    MARKETAUX_API_KEY = os.getenv("MARKETAUX_API_KEY", "")
    LLM_MODEL = os.getenv("LLM_MODEL", "llama-3.3-70b-versatile")
    EMBED_MODEL = os.getenv("EMBED_MODEL", "all-MiniLM-L6-v2")

settings = Settings()
