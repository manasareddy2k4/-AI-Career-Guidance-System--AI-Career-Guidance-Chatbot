"""
backend/api.py — FastAPI main server
Run with: uvicorn backend.api:app --reload --port 8000
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.routes import chat, gap_analysis, resume, panel

app = FastAPI(
    title       = "AI Career Co-Pilot API",
    description = "Backend API for career guidance, gap analysis, resume parsing and chatbot",
    version     = "1.0.0",
)

# Allow Streamlit frontend to call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins     = ["http://localhost:8501"],
    allow_credentials = True,
    allow_methods     = ["*"],
    allow_headers     = ["*"],
)

# Register all routes
app.include_router(chat.router,         tags=["Chat"])
app.include_router(gap_analysis.router, tags=["Gap Analysis"])
app.include_router(resume.router,       tags=["Resume"])
app.include_router(panel.router,        tags=["Panel & Job Links"])

@app.get("/health", tags=["Health"])
def health():
    return {"status": "running", "message": "AI Career Co-Pilot API is live"}

@app.get("/", tags=["Health"])
def root():
    return {
        "message": "AI Career Co-Pilot API",
        "docs":    "http://localhost:8000/docs",
        "health":  "http://localhost:8000/health",
    }
