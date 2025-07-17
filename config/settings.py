# config/settings.py
import os
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict



# Only try to load a .env file if we are in a local environment
if os.getenv("EXECUTION_ENVIRONMENT") != "docker":
    from dotenv import load_dotenv
    print(">>> RUNNING IN LOCAL MODE: Loading .env.local file. <<<")
    # This will now ONLY run when you execute the script on your Mac,
    # because the EXECUTION_ENVIRONMENT variable won't be set.
    load_dotenv(".env.local", override=True)
# -------------------------------------------------------------------    


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