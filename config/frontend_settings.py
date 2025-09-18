# config/frontend_settings.py
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict

class FrontendSettings(BaseSettings):
    BACKEND_URL: str = "http://localhost:8000"
    model_config = SettingsConfigDict(case_sensitive=True)

@lru_cache()
def get_frontend_settings():
    return FrontendSettings()
