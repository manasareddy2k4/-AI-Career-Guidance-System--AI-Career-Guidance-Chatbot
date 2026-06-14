"""
backend/routes/resume.py
POST /parse-resume — extract structured data from resume text
"""

import json
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from backend.services.ai_service import single_prompt

router = APIRouter()

class ResumeRequest(BaseModel):
    text: str   # raw text already extracted from PDF by frontend

class ResumeResponse(BaseModel):
    name:             str  = ""
    email:            str  = ""
    degrees:          list = []
    certifications:   list = []
    skills:           list = []
    job_titles:       list = []
    years_experience: int  = 0

PROMPT = """You are a resume parser. Extract information from this resume text.
Return ONLY valid JSON — no markdown, no extra text:
{{
  "name": "",
  "email": "",
  "degrees": [],
  "certifications": [],
  "skills": [],
  "job_titles": [],
  "years_experience": 0
}}

Resume:
{text}"""

@router.post("/parse-resume", response_model=ResumeResponse)
def parse_resume(req: ResumeRequest):
    try:
        raw = single_prompt(PROMPT.format(text=req.text[:4000]), temperature=0.1)
        raw = raw.strip()
        if raw.startswith("```"):
            raw = "\n".join(
                l for l in raw.splitlines()
                if not l.strip().startswith("```")
            ).strip()
        data = json.loads(raw)
        return ResumeResponse(**data)
    except json.JSONDecodeError:
        raise HTTPException(status_code=422, detail="Could not parse resume — try again")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
