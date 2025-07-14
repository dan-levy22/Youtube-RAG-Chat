# In create_tables.py
from sqlmodel import SQLModel, create_engine
import os
# Import from our new, isolated config file
from db_config import DATABASE_URL

# IMPORTANT: Import all your SQLModel table models here
from db.models import *

print("--- Connecting to database to create tables ---")
print(f"DATABASE_URL used: {DATABASE_URL.replace(os.getenv('DB_PASSWORD'), '***')}") # Hide password in log

try:
    engine = create_engine(DATABASE_URL)
    SQLModel.metadata.create_all(engine)
    print("✅ Tables created successfully!")
except Exception as e:
    print("❌ An error occurred while creating tables:")
    print(e)