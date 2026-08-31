"""
Central application configuration.

All tunable values live here so the rest of the codebase never hardcodes
paths, timeouts, or limits. Values can be overridden via a local .env file
(see .env.example) without touching source code.
"""
from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

                                                                  
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")


def _env_bool(name: str, default: bool) -> bool:
    val = os.getenv(name)
    if val is None:
        return default
    return val.strip().lower() in {"1", "true", "yes", "on"}


def _env_int(name: str, default: int) -> int:
    val = os.getenv(name)
    if val is None:
        return default
    try:
        return int(val)
    except ValueError:
        return default


class Settings:
    """Application-wide settings, resolved once at import time."""

                                                                       
    BASE_DIR: Path = BASE_DIR
    DATA_DIR: Path = BASE_DIR / "data"
    DATABASE_PATH: Path = DATA_DIR / "osint_dashboard.db"
    DATABASE_URL: str = f"sqlite:///{DATABASE_PATH}"

                                                                         
    APP_NAME: str = "OSINT Research Dashboard"
    APP_VERSION: str = "1.0.0"

                                                                          
    USER_AGENT: str = os.getenv(
        "OSINT_USER_AGENT",
        "OSINT-Research-Dashboard/1.0 (Educational Research Tool; +https://github.com)",
    )
    REQUEST_TIMEOUT_SECONDS: int = _env_int("OSINT_REQUEST_TIMEOUT", 10)
    REQUEST_DELAY_SECONDS: float = float(os.getenv("OSINT_REQUEST_DELAY", "1.0"))
    MAX_RETRIES: int = _env_int("OSINT_MAX_RETRIES", 2)
    RESPECT_ROBOTS_TXT: bool = _env_bool("OSINT_RESPECT_ROBOTS", True)

                                                                          
    DEPTH_LIMITS = {
        "quick": {"max_sources": 8, "max_news_items": 5},
        "standard": {"max_sources": 20, "max_news_items": 12},
        "deep": {"max_sources": 40, "max_news_items": 25},
    }

                                                                           
                                                                            
                                                                         
    NEWSAPI_KEY: str | None = os.getenv("NEWSAPI_KEY") or None

                                                                           
    CACHE_TTL_SECONDS: int = _env_int("OSINT_CACHE_TTL", 3600)

                                                                       
    THEME_PRIMARY: str = "#5B8DEF"
    THEME_BACKGROUND: str = "#0E1117"
    THEME_SECONDARY_BG: str = "#161B22"
    THEME_TEXT: str = "#E6E6E6"
    THEME_MUTED: str = "#8B949E"
    THEME_SUCCESS: str = "#3FB950"
    THEME_WARNING: str = "#D29922"
    THEME_DANGER: str = "#F85149"


settings = Settings()

                                              
settings.DATA_DIR.mkdir(parents=True, exist_ok=True)
