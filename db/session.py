from sqlmodel import Session, create_engine
import logging

from config.settings import get_settings

logger = logging.getLogger(__name__)
engine = None

def get_session():
    global engine
    if engine is None:
        settings = get_settings()
        
        # Mask password in logs
        safe_url = settings.DATABASE_URL.replace(
            settings.DB_PASSWORD, 
            '*****'
        )
        logger.info(f"Creating database connection to: {safe_url}")
        
        try:
            engine = create_engine(settings.DATABASE_URL)
            logger.info("✅ Database connection successful")
        except Exception as e:
            logger.error(f"❌ Database connection failed: {str(e)}")
            raise

    with Session(engine) as session:
        yield session