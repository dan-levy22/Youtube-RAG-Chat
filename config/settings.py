# config/settings.py
import os
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv

# --- The Key Addition ---
# This line will find the .env file in your project root and load its variables
# into the environment, making them available to Pydantic below.
load_dotenv()
# ----------------------


class Settings(BaseSettings):
    # Variables that MUST be in the environment (or .env file)
    DATABASE_URL: str
    GEMINI_API_KEY: str
    PROXY_URL: str | None = None

    # Variables with defaults that can be overridden
    BACKEND_URL: str = "http://localhost:8000"
    CHROMA_HOST: str = "localhost"
    CHROMA_PORT: int = 8000

    model_config = SettingsConfigDict(case_sensitive=True)


@lru_cache()
def get_settings():
    return Settings()

settings = get_settings()