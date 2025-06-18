import logging
from urllib.parse import parse_qs, urlparse
import traceback
import os
import json

from youtube_transcript_api import YouTubeTranscriptApi, NoTranscriptFound
from yt_dlp import YoutubeDL  # for metadata
from langchain.schema import Document
from sqlmodel import Session

from app.core.logging_setup import setup_logging
from db.crud import load_transcript, save_transcript
from config.settings import settings

# Set up logger
setup_logging()

logger = logging.getLogger(__name__)


def extract_video_id(video_url: str) -> str:
    # Normalise to a build-in str
    video_url = str(video_url)
    
    video_id: str | None = None

    parsed = urlparse(video_url)
    # youtu.be/XYZ
    if parsed.netloc.endswith("youtu.be"):
        video_id = parsed.path.lstrip("/")
    # youtube.com/watch?v=XYZ
    else: 
        video_id = parse_qs(parsed.query).get("v", [None])[0]

    if not video_id:
        logger.error(f"Failed to extract video_id from URL: {video_url}")
        raise ValueError(f"Invalid Youtube URL, could not parse video_id: {video_url}")

    # Assertion that video_id is a string- tells mypy that video_id is not None
    assert video_id is not None

    return video_id

def get_transcript(video_url: str, db: Session) -> list[Document]:
    """
    Return a list of Document chunks for this video using yt-dlp for everything.

    - If cached, returns the transcript from the database.
    - Otherwise, uses yt-dlp to fetch both metadata and the transcript file.
    - On success, it saves the new transcript to the cache and returns it.
    - On failure, it logs the error and returns an empty list.
    """
    video_id = extract_video_id(video_url)
    clean_url = f"https://www.youtube.com/watch?v={video_id}"

    # 1. Check for a cached version first.
    cache = load_transcript(db, video_id)
    if cache is not None:
        logger.info(f"Transcript for {video_id} found in cache. Returning from DB.")
        return [Document(page_content=cache.transcript, metadata=cache.doc_metadata or {})]

    logger.info(f"Transcript not in cache for {video_id}. Fetching via yt-dlp.")
    
    # The filename yt-dlp will create, using a temporary directory is best practice
    transcript_filename = f"{video_id}.en.json3"
    
    ydl_opts = {
        'writesubtitles': True,
        'writeautomaticsub': True,
        'subtitleslangs': ['en', 'en-US'],
        'skip_download': True,
        'outtmpl': f'{video_id}', # Just the ID, extension is added automatically
        'subtitlesformat': 'json3',
        'quiet': True,
        'proxy': settings.PROXY_URL or None # Use proxy if available
    }

    try:
        # --- Step A & B: Get Metadata and Transcript File with yt-dlp ---
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(clean_url, download=False)
            # Now, trigger the download of the subtitle file
            ydl.download([clean_url])

        # Check if the transcript file was actually created
        if not os.path.exists(transcript_filename):
            raise NoTranscriptFound(video_id, ['en', 'en-US'], 'yt-dlp did not download a transcript file.')

        # --- Step C: Process the downloaded file ---
        with open(transcript_filename, 'r', encoding='utf-8') as f:
            data = json.load(f)

        full_transcript_text = " ".join(
            event['segs'][0]['utf8'] 
            for event in data.get('events', []) 
            if 'segs' in event and event['segs'] and 'utf8' in event['segs'][0]
        ).strip()
        
        logger.info(f"Successfully fetched transcript for {video_id} ({len(full_transcript_text)} chars).")

        video_metadata = {
            "source": video_id,
            "title": info.get("title", "Unknown Title"),
            "uploader": info.get("uploader", "Unknown Uploader"),
            "upload_date": info.get("upload_date"),
            "video_id": video_id,
        }
        
        docs = [Document(page_content=full_transcript_text, metadata=video_metadata)]
        
        # --- Step D: Save to cache ---
        save_transcript(db=db, video_id=video_id, title=video_metadata["title"], transcript=full_transcript_text, metadata=video_metadata)
        
        return docs
    
    except NoTranscriptFound:
        logger.warning(f"No English transcript found for video_id: {video_id}.")
        save_transcript(db=db, video_id=video_id, title="Transcript Not Available", transcript="", metadata={"video_id": video_id})
        return []
        
    except Exception as e:
        logger.error(f"An unexpected yt-dlp error occurred for {video_id}: {e}", exc_info=True)
        traceback.print_exc()
        return []
    
    finally:
        # --- Step E: Always clean up the downloaded file ---
        if os.path.exists(transcript_filename):
            os.remove(transcript_filename)
            logger.info(f"Cleaned up temporary file '{transcript_filename}'.")


# def get_transcript(video_url: str, db: Session) -> list[Document]:
#     """
#     Return a list of Document chunks for this video using the hybrid best-of-breed approach.

#     - If cached, returns the transcript from the database wrapped in a Document.
#     - Otherwise, fetches fresh data:
#         - Uses youtube-transcript-api for the transcript text.
#         - Uses yt-dlp for the video metadata.
#     - On success, it saves the new transcript to the cache and returns it.
#     - On failure, it logs the error and returns an empty list.
#     """
#     # 1. Check for a cached version in the database first.
#     video_id = extract_video_id(video_url)
#     clean_url = f"https://www.youtube.com/watch?v={video_id}"
#     cache = load_transcript(db, video_id)
#     if cache is not None:
#         logger.info(f"Transcript for {video_id} found in cache. Returning from DB.")
#         # Reconstruct the Document object from cached data.
#         return [
#             Document(
#                 page_content=cache.transcript,
#                 metadata=cache.doc_metadata or {},
#             )
#         ]

#     logger.info(f"Transcript not in cache for {video_id}. Fetching from source.")

#     # --- This is the key change ---
#     # Create the proxies dictionary for youtube-transcript-api
#     proxies = {}
#     # Get the proxy URL for yt-dlp
#     proxy_for_yt_dlp = None

#     if settings.PROXY_URL:
#         proxies = {"http": settings.PROXY_URL, "https": settings.PROXY_URL}
#         proxy_for_yt_dlp = settings.PROXY_URL
#         logger.info("Using proxy for all YouTube requests.")

#     # 2. Fetch fresh data from YouTube using our robust, hybrid method.
#     try:
#         # --- Step A: Get Metadata with yt-dlp ---
#         # This is more reliable than pytube for metadata.
#         ydl_opts = {
#             "quiet": True, 
#             "skip_download": True,
#             "proxy": proxy_for_yt_dlp
#             }
#         with YoutubeDL(ydl_opts) as ydl:
#             info = ydl.extract_info(clean_url, download=False)
        
#         video_metadata = {
#             "source": video_id, # Use video_id as the source identifier
#             "title": info.get("title", "Unknown Title"),
#             "uploader": info.get("uploader", "Unknown Uploader"),
#             "upload_date": info.get("upload_date"),
#             "video_id": video_id,
#         }
#         logger.info(f"Successfully fetched metadata for '{video_metadata['title']}'")

#         # --- Step B: Get Transcript with youtube-transcript-api ---
#         # This is proven to work and gets the best quality transcript.
#         transcript_list = YouTubeTranscriptApi.get_transcript(
#             video_id,
#             proxies=proxies, 
#             languages=['en', 'en-US']
#             )
#         full_transcript_text = " ".join([item['text'] for item in transcript_list])
#         logger.info(f"Successfully fetched transcript for {video_id} ({len(full_transcript_text)} chars).")

#         # --- Step C: Combine and Create Document ---
#         # Now that we have all data, create the final Document object.
#         docs = [
#             Document(
#                 page_content=full_transcript_text,
#                 metadata=video_metadata
#             )
#         ]
        
#         # --- Step D: Save the new transcript to the cache ---
#         save_transcript(
#             db=db,
#             video_id=video_id,
#             title=video_metadata["title"],
#             transcript=full_transcript_text,
#             metadata=video_metadata
#         )
        
#         return docs
    
#     except NoTranscriptFound:
#         logger.warning(f"No English transcript found for video_id: {video_id}. This is a valid outcome, not an error.")
#         # It's important to cache this "not found" result to avoid re-fetching.
#         # We can save an empty transcript.
#         save_transcript(
#             db=db, video_id=video_id, title="Transcript Not Available", 
#             transcript="", metadata={"video_id": video_id}
#         )
#         return [] # Return empty list as required
        
#     except Exception as e:
#         # Catch any other unexpected errors during the process.
#         logger.error(f"An unexpected error occurred while fetching data for {video_id}: {e}", exc_info=True)
#         traceback.print_exc()
#         return [] # Return empty list on any failure to satisfy typing.