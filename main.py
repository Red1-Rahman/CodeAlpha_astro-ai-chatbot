import os
import logging
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from dotenv import load_dotenv

# Using logging instead of print; logger.exception gives full traceback
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# Load env vars from .env if present
load_dotenv()

# Import core logic (matcher + formatter)
from chatbot.matcher import matcher
from chatbot.response_builder import format_response

# Absolute base path so paths don’t break across OS or run context
BASE_DIR = Path(__file__).resolve().parent

app = FastAPI(title="Astro-AI FAQ Chatbot")

# Request model with basic validation (no empty/spam inputs)
class ChatRequest(BaseModel):
    query: str = Field(min_length=1, max_length=500)

# Response model so FastAPI validates + documents output schema
class ChatResponse(BaseModel):
    answer: str
    score: float
    related_questions: list

# Mount frontend assets using absolute path
app.mount("/assets", StaticFiles(directory=BASE_DIR / "frontend"), name="assets")

# Serve main UI from absolute path
@app.get("/")
async def serve_frontend():
    return FileResponse(BASE_DIR / "frontend/index.html")

# Main API endpoint (match → format → return)
@app.post("/api/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """
    Run matcher, format response, return to frontend.
    """
    try:
        raw_match = matcher.get_best_match(request.query)
        final_payload = format_response(raw_match, request.query)
        return final_payload
    except Exception as e:
        # Log full error for debugging
        logger.exception("Chat endpoint failed") 
        
        # Return proper 500 instead of fake success
        raise HTTPException(
            status_code=500,
            detail="Something went wrong on our side."
        )

if __name__ == "__main__":
    import uvicorn
    # Run locally with auto-reload
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)