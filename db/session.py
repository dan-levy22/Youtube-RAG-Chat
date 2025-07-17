from sqlmodel import Session, create_engine

from config.settings import settings

engine = create_engine(url= settings.DATABASE_URL)

def get_session():
    with Session(engine) as session:
        yield session