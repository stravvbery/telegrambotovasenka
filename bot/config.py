import os
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv
from pydantic import BaseModel, Field

ENV_PATH = Path(__file__).resolve().parent.parent / ".env"
if ENV_PATH.exists():
    load_dotenv(ENV_PATH)


class Settings(BaseModel):
    bot_token: str = ""
    fireworks_api_key: str = ""
    gemini_api_keys: list[str] = Field(default_factory=list)
    tavily_api_key: str = ""
    firecrawl_api_key: str = ""
    serpapi_key: str = ""
    default_model: str = "gemini-flash"


def _parse_csv(value: str | None) -> list[str]:
    if not value:
        return []
    return [part.strip() for part in value.split(",") if part.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings(
        bot_token=os.getenv("BOT_TOKEN", ""),
        fireworks_api_key=os.getenv("FIREWORKS_API_KEY", ""),
        gemini_api_keys=_parse_csv(os.getenv("GEMINI_API_KEYS")),
        tavily_api_key=os.getenv("TAVILY_API_KEY", ""),
        firecrawl_api_key=os.getenv("FIRECRAWL_API_KEY", ""),
        serpapi_key=os.getenv("SERPAPI_KEY", ""),
        default_model=os.getenv("DEFAULT_MODEL", "gemini-flash"),
    )


def validate_settings(settings: Settings) -> None:
    missing = []
    if not settings.bot_token:
        missing.append("BOT_TOKEN")
    if not settings.fireworks_api_key:
        missing.append("FIREWORKS_API_KEY")
    if not settings.gemini_api_keys:
        missing.append("GEMINI_API_KEYS")

    if missing:
        raise RuntimeError(
            "Missing required environment variables: " + ", ".join(missing)
        )
