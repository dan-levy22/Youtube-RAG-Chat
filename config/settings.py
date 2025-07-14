# config/settings.py
import os
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, computed_field
from sqlalchemy import URL



# Only try to load a .env file if we are in a local environment
if os.getenv("EXECUTION_ENVIRONMENT") != "docker":
    from dotenv import load_dotenv
    print(">>> RUNNING IN LOCAL MODE: Loading .env.local file. <<<")
    # This will now ONLY run when you execute the script on your Mac,
    # because the EXECUTION_ENVIRONMENT variable won't be set.
    load_dotenv(".env.local", override=True)
# -------------------------------------------------------------------    


class Settings(BaseSettings):
    # --- Required variables loaded from the environment ---
    # Use repr=False to prevent secrets from being printed in logs
    DB_USER: str
    DB_PASSWORD: str = Field(repr=False)
    DB_HOST: str
    DB_PORT: int = 5432
    DB_NAME: str
    GEMINI_API_KEY: str = Field(repr=False)

    # --- Optional variables ---
    PROXY_URL: str | None = None

    # Variables with defaults that can be overridden
    BACKEND_URL: str = "http://localhost:8000"
    CHROMA_HOST: str = "localhost"
    CHROMA_PORT: int = 8000

    # --- A computed field to build the database URL ---
    @computed_field
    @property
    def DATABASE_URL(self) -> str:
        # Using SQLAlchemy's URL object is robust, but a simple f-string also works
        # return f"postgresql+psycopg2://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        return str(URL.create(
            drivername="postgresql+psycopg2",
            username=self.DB_USER,
            password=self.DB_PASSWORD,
            host=self.DB_HOST,
            port=self.DB_PORT,
            database=self.DB_NAME,
            query={"sslmode": "require"}
        ))
    
    model_config = SettingsConfigDict(case_sensitive=True)


@lru_cache()
def get_settings():
    return Settings()

# settings = get_settings()