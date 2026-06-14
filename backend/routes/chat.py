"""
backend/routes/chat.py
POST /chat — career chatbot endpoint
"""

import re
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from backend.services.ai_service import chat_completion

router = APIRouter()

# ── Request / Response models ─────────────────────────────────────────────────
class ChatRequest(BaseModel):
    message:  str
    history:  list[dict] = []   # [{"role":"user/assistant","content":"..."}]
    profile:  dict        = {}
    gap:      dict        = {}
    language: str         = "English"

class ChatResponse(BaseModel):
    reply:      str
    panel_type: str | None = None   # "interview_guide" | "skill_roadmap" | "job_links" | "courses"

# ── System prompt ─────────────────────────────────────────────────────────────
SYSTEM = """You are an AI Career Co-Pilot — a friendly, expert career advisor.
You help people plan careers in ANY field: tech, finance, law, medicine, design, business, and more.
Respond in {language}.

Student profile: {profile}
Skill gap results: {gap}

Rules:
- Give warm, specific, actionable advice
- Use bullet points and clear structure
- Cover any career field — never say you only handle tech
- If no profile yet, gently suggest filling the intake form in the sidebar
- When asked for interview guide    → end response with [PANEL:interview_guide]
- When asked for skill roadmap      → end response with [PANEL:skill_roadmap]
- When asked for job links/search   → end response with [PANEL:job_links]
- When asked for courses/resources  → end response with [PANEL:courses]
- For salary questions about AI/tech roles, use figures from gap results if available
"""

@router.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    try:
        system_content = SYSTEM.format(
            language=req.language,
            profile=str(req.profile) if req.profile else "Not provided yet.",
            gap=str(req.gap)         if req.gap     else "Not run yet.",
        )

        messages = [{"role": "system", "content": system_content}]

        # Add conversation history
        for msg in req.history[-10:]:   # last 10 messages to stay within token limit
            messages.append({
                "role":    msg.get("role", "user"),
                "content": msg.get("content", ""),
            })

        # Add current message
        messages.append({"role": "user", "content": req.message})

        raw_reply  = chat_completion(messages)

        # Extract panel tag if present
        panel_match = re.search(r"\[PANEL:(\w+)\]", raw_reply)
        panel_type  = panel_match.group(1) if panel_match else None
        clean_reply = re.sub(r"\[PANEL:\w+\]", "", raw_reply).strip()

        return ChatResponse(reply=clean_reply, panel_type=panel_type)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
