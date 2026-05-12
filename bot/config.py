import os
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv
from pydantic import BaseModel

load_dotenv(Path(__file__).parent.parent / ".env")


class Settings(BaseModel):
    bot_token: str
    fireworks_api_key: str
    gemini_api_keys: list[str] = []
    tavily_api_key: str = ""
    firecrawl_api_key: str = ""
    serpapi_key: str = ""
    default_model: str = "gemini-flash"


@lru_cache
def get_settings() -> Settings:
    gemini_raw = os.getenv("GEMINI_API_KEYS", "")
    gemini_keys = [k.strip() for k in gemini_raw.split(",") if k.strip()]

    return Settings(
        bot_token=os.getenv("BOT_TOKEN", ""),
        fireworks_api_key=os.getenv("FIREWORKS_API_KEY", ""),
        gemini_api_keys=gemini_keys,
        tavily_api_key=os.getenv("TAVILY_API_KEY", ""),
        firecrawl_api_key=os.getenv("FIRECRAWL_API_KEY", ""),
        serpapi_key=os.getenv("SERPAPI_KEY", ""),
        default_model=os.getenv("DEFAULT_MODEL", "gemini-flash"),
    )
