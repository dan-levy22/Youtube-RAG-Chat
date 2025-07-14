# from sqlmodel import Session, create_engine

# from config.settings import settings

# # engine = create_engine(url= settings.DATABASE_URL)

# # def get_session():
# #     with Session(engine) as session:
# #         yield session

# engine = None

# def get_session():
#     global engine
#     if engine is None:
#         # This block will only run once, on the very first API call that needs a DB connection
#         print("--- Database engine does not exist. Creating it now. ---")
#         engine = create_engine(url= settings.DATABASE_URL)
    
#     with Session(engine) as session:
#         yield session

# In db/session.py
from sqlmodel import Session, create_engine

engine = None

def get_session():
    global engine
    if engine is None:
        # Import the function here
        from config.settings import get_settings
        # Call the function to get fresh settings
        settings = get_settings()
        print("--- Database engine does not exist. Creating it now. ---")
        engine = create_engine(url=settings.DATABASE_URL)

    with Session(engine) as session:
        yield session