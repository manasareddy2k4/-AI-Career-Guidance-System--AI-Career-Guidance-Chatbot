"""
frontend/modules/api_client.py
All HTTP calls to the FastAPI backend live here.
Frontend never calls Groq directly — always goes through the API.
"""

import requests
import streamlit as st
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from config import API_BASE_URL

TIMEOUT = 60  # seconds

def _post(endpoint: str, payload: dict) -> dict | None:
    """POST helper with error handling."""
    try:
        r = requests.post(f"{API_BASE_URL}{endpoint}", json=payload, timeout=TIMEOUT)
        r.raise_for_status()
        return r.json()
    except requests.exceptions.ConnectionError:
        st.error("❌ Cannot connect to API. Make sure the backend is running:\n`uvicorn backend.api:app --reload --port 8000`")
        return None
    except requests.exceptions.Timeout:
        st.error("⏳ API request timed out. Try again.")
        return None
    except requests.exceptions.HTTPError as e:
        detail = e.response.json().get("detail", str(e)) if e.response else str(e)
        st.error(f"❌ API error: {detail}")
        return None

def _get(endpoint: str, params: dict = {}) -> dict | None:
    """GET helper with error handling."""
    try:
        r = requests.get(f"{API_BASE_URL}{endpoint}", params=params, timeout=TIMEOUT)
        r.raise_for_status()
        return r.json()
    except requests.exceptions.ConnectionError:
        st.error("❌ Cannot connect to API. Start backend first.")
        return None
    except Exception as e:
        st.error(f"❌ API error: {e}")
        return None

# ── Public API functions ──────────────────────────────────────────────────────

def send_chat(message: str, history: list, profile: dict,
              gap: dict, language: str) -> dict | None:
    """POST /chat"""
    return _post("/chat", {
        "message":  message,
        "history":  history,
        "profile":  profile,
        "gap":      gap,
        "language": language,
    })

def run_gap_analysis(target_role: str, skills_known: str,
                     resume_skills: list) -> dict | None:
    """POST /gap-analysis"""
    return _post("/gap-analysis", {
        "target_role":   target_role,
        "skills_known":  skills_known,
        "resume_skills": resume_skills,
    })

def parse_resume_text(text: str) -> dict | None:
    """POST /parse-resume"""
    return _post("/parse-resume", {"text": text})

def get_panel_content(panel_type: str, role: str,
                      skills: str, language: str) -> dict | None:
    """POST /panel"""
    return _post("/panel", {
        "panel_type": panel_type,
        "role":       role,
        "skills":     skills,
        "language":   language,
    })

def get_job_links(role: str, location: str) -> dict | None:
    """GET /job-links"""
    return _get("/job-links", {"role": role, "location": location})

def check_health() -> bool:
    """GET /health — returns True if API is running."""
    try:
        r = requests.get(f"{API_BASE_URL}/health", timeout=5)
        return r.status_code == 200
    except Exception:
        return False
