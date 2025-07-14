import logging

from app.core.logging_setup import configure_logging

# Set up logging
configure_logging(level = 10)

logger = logging.getLogger()

from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session, SQLModel, create_engine


from app.api.routers.chat import router as chat_router
from app.api.routers.session import router as session_router
from app.api.routers.summary import router as summary_router
from app.backend_schemas import PreviousConversationItem, PreviousConversationsResponse
from db.crud import get_video_ids_and_titles_by_user_id
from db.session import engine, get_session
from config.settings import get_settings



@asynccontextmanager
async def lifespan(app: FastAPI):
    #  # This code runs on startup
    print("--- Application starting up... ---")
    # settings=get_settings()
    # print("DB URL:", settings.DATABASE_URL)
    # print("DB_USER:", settings.DB_USER)
    # print("DB_PASSWORD", settings.DB_PASSWORD)
    # print("DB_HOST", settings.DB_HOST)
    # print("DB_PORT", settings.DB_PORT)
    # print("DB_NAME", settings.DB_NAME)
    # print("BACKEND_URL", settings.BACKEND_URL)
    
    yield
    print("--- Application shutting down... ---")
    
    # print("--- Lifespan startup: Creating database engine... ---")
    # # print("Creating database tables...")
    # # try:
    # #     # Create all tables based on your SQLModel models
    # #     SQLModel.metadata.create_all(engine)
    # #     print("Database tables created successfully.")
    # # except Exception as e:
    # #     print(f"An error occurred while creating database tables: {e}")

    # yield
    
    # # This code runs on shutdown
    # print("--- Lifespan shutdown: Disposing of database engine... ---")
    # app.state.db_engine.dispose()


app = FastAPI(
    title="Youtube RAG Chat",
    version= "0.1.0",
    lifespan=lifespan, 
    debug=True
)

# configure_logging(level=logging.DEBUG)
# logging.getLogger("httpx").setLevel(logging.WARNING)

app.add_middleware(
    CORSMiddleware,
    allow_origins = ["http://localhost:8501"], # Trust front-end on port 8501
    allow_methods = ["*"],                     # HTTP actions/ verbs permitted
    allow_headers = ["*"],                     # HTTP headers permitted
    allow_credentials=True                     # Allow sending credentials (includes cookies)
)

# mount router under /api
app.include_router(summary_router, prefix="/api")
app.include_router(chat_router, prefix="/api")
app.include_router(session_router, prefix="/api")

@app.get("/api/users/{user_id}/conversations", response_model=PreviousConversationsResponse)
def get_past_conversations(
    user_id: str,
    db: Session = Depends(get_session), 
    ) -> PreviousConversationsResponse:
    try:
        results = get_video_ids_and_titles_by_user_id(db=db, target_user_id=user_id)
    except Exception as e:
        logger.exception("❌ rag_chat_service failed")
        raise HTTPException(status_code=502, detail=str(e)) from e
    
    # Convert to PreviousConversationsResponse pydantic model
    conversation_items = [PreviousConversationItem(video_id=video_id, title=title) for video_id, title in results]
    final_response = PreviousConversationsResponse(conversations=conversation_items)
    return final_response

@app.get("/health", status_code=200)
def health_check():
    """A simple endpoint to confirm the service is running."""
    return {"status": "ok", "message": "Backend service is alive!"}

if __name__ == "__main__":
    import uvicorn

    from app.core.logging_setup import configure_logging
    

    uvicorn.run(
        app="app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_config=None,
        log_level=10
    )