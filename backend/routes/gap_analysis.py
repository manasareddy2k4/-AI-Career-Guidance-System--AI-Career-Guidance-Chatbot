"""
backend/routes/gap_analysis.py
POST /gap-analysis — silent skill gap analyzer
"""

import json
import sys
import os
import pandas as pd
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from backend.services.ai_service import single_prompt
from config import DATASET_PATH

router = APIRouter()

class GapRequest(BaseModel):
    target_role:   str
    skills_known:  str  = ""
    resume_skills: list = []

class GapResponse(BaseModel):
    readiness_score: int   = 0
    missing_skills:  list  = []
    strengths:       list  = []
    roadmap_summary: str   = ""
    data_source:     str   = ""

# ── Prompts ───────────────────────────────────────────────────────────────────
DATASET_PROMPT = """You are a career advisor. A student wants to become a "{role}".
Current skills: {skills}
Job market data from dataset: {jobs}

Return ONLY valid JSON, no markdown:
{{
  "readiness_score": 6,
  "missing_skills": [{{"skill": "X", "resource": "free resource", "months_to_learn": 2}}],
  "strengths": ["skill1"],
  "roadmap_summary": "Two sentences on path forward.",
  "data_source": "AI Jobs Market Dataset 2025-2026"
}}"""

FALLBACK_PROMPT = """You are a career advisor. A student wants to become a "{role}".
Current skills: {skills}

Return ONLY valid JSON, no markdown:
{{
  "readiness_score": 6,
  "missing_skills": [{{"skill": "X", "resource": "free resource", "months_to_learn": 2}}],
  "strengths": ["skill1"],
  "roadmap_summary": "Two sentences on path forward.",
  "data_source": "Groq AI knowledge (role not found in dataset)"
}}"""

def _load_jobs(role: str) -> list:
    try:
        df   = pd.read_csv(DATASET_PATH)
        mask = df["job_title"].str.contains(role, case=False, na=False)
        sub  = df[mask].head(10)
        if sub.empty:
            mask2 = df["job_category"].str.contains(role, case=False, na=False)
            sub   = df[mask2].head(10)
        return sub[["job_title","required_skills","annual_salary_usd"]].to_dict("records")
    except Exception:
        return []

def _parse_json(raw: str) -> dict:
    raw = raw.strip()
    if raw.startswith("```"):
        raw = "\n".join(
            l for l in raw.splitlines()
            if not l.strip().startswith("```")
        ).strip()
    return json.loads(raw)

@router.post("/gap-analysis", response_model=GapResponse)
def gap_analysis(req: GapRequest):
    try:
        manual = [s.strip() for s in req.skills_known.split(",") if s.strip()]
        skills = list(set(manual + req.resume_skills))
        jobs   = _load_jobs(req.target_role)

        if jobs:
            prompt = DATASET_PROMPT.format(
                role=req.target_role,
                skills=json.dumps(skills),
                jobs=json.dumps(jobs, indent=2)[:2500],
            )
        else:
            prompt = FALLBACK_PROMPT.format(
                role=req.target_role,
                skills=json.dumps(skills),
            )

        raw    = single_prompt(prompt, temperature=0.1)
        result = _parse_json(raw)
        return GapResponse(**result)

    except json.JSONDecodeError:
        raise HTTPException(status_code=422, detail="AI returned invalid JSON — try again")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
