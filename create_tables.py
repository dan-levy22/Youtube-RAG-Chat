# In create_tables.py
from sqlmodel import SQLModel, create_engine
from sqlalchemy import inspect
import os
# Import from our new, isolated config file
from config.settings import get_settings

settings = get_settings()
DATABASE_URL = settings.DATABASE_URL

# IMPORTANT: Import all your SQLModel table models here
from db.models import *

print("--- Connecting to database to create tables ---")
pwd = os.getenv("DB_PASSWORD", "")
safe_url = DATABASE_URL.replace(pwd, "***") if pwd else DATABASE_URL
print(f"DATABASE_URL used: {DATABASE_URL.replace(os.getenv('DB_PASSWORD'), '***')}") # Hide password in log

try:
    engine = create_engine(DATABASE_URL, pool_pre_ping=True)
    SQLModel.metadata.create_all(engine)
    print("✅ Tables created successfully!")
    print("Tables now present:", inspect(engine).get_table_names())
except Exception as e:
    print("❌ An error occurred while creating tables:")
    print(e)