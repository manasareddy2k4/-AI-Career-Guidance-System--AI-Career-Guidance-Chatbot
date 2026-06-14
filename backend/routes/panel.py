"""
backend/routes/panel.py
POST /panel — generate right-panel content (interview guide, roadmap, courses)
GET  /job-links — build LinkedIn + Naukri search URLs
"""

import sys
import os
from urllib.parse import quote_plus
from fastapi import APIRouter
from pydantic import BaseModel

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from backend.services.ai_service import single_prompt
from config import INDIA_LOCATIONS

router = APIRouter()

# ── Panel content ─────────────────────────────────────────────────────────────
class PanelRequest(BaseModel):
    panel_type: str          # interview_guide | skill_roadmap | courses
    role:       str  = ""
    skills:     str  = ""
    language:   str  = "English"

class PanelResponse(BaseModel):
    content: str
    title:   str

PROMPTS = {
    "interview_guide": """Generate a detailed interview prep guide for a "{role}" role.
Sections: Week 1 Fundamentals, Week 2 Applied Practice, Week 3 Mock Interviews, Week 4 Company Research, Final Tips.
Include technical topics, behavioural questions (STAR method), and free mock interview resources.
Respond in {language}. Use markdown.""",

    "skill_roadmap": """Generate a week-by-week learning roadmap for someone becoming a "{role}".
Current skills: {skills}
Format: Week 1-2 | Week 3-4 | Month 2 | Month 3 | Month 4+
Include free resources for each stage.
Respond in {language}. Use markdown.""",

    "courses": """List the top 10 free or affordable courses for someone wanting to become a "{role}".
Format as a markdown table: | Course | Platform | Duration | Cost |
Respond in {language}.""",
}

TITLES = {
    "interview_guide": "🎯 Interview Prep Guide",
    "skill_roadmap":   "📚 Skill Learning Roadmap",
    "courses":         "🎓 Recommended Courses",
}

@router.post("/panel", response_model=PanelResponse)
def generate_panel(req: PanelRequest):
    prompt_template = PROMPTS.get(req.panel_type, "")
    if not prompt_template:
        return PanelResponse(content="Unknown panel type.", title="")

    prompt  = prompt_template.format(
        role=req.role, skills=req.skills, language=req.language
    )
    content = single_prompt(prompt, temperature=0.5)
    title   = TITLES.get(req.panel_type, "📋 Details")
    return PanelResponse(content=content, title=title)

# ── Job links ─────────────────────────────────────────────────────────────────
class JobLinksResponse(BaseModel):
    linkedin: str
    naukri:   str | None = None
    is_india: bool       = False

@router.get("/job-links", response_model=JobLinksResponse)
def job_links(role: str, location: str):
    role_enc     = quote_plus(role)
    location_enc = quote_plus(location)
    linkedin     = f"https://www.linkedin.com/jobs/search/?keywords={role_enc}&location={location_enc}"

    india = any(loc in location.lower() for loc in INDIA_LOCATIONS)
    naukri = None
    if india:
        role_slug     = role.lower().replace(" ", "-")
        location_slug = location.lower().replace(" ", "-")
        naukri        = f"https://www.naukri.com/{role_slug}-jobs-in-{location_slug}"

    return JobLinksResponse(linkedin=linkedin, naukri=naukri, is_india=india)
