"""
frontend/modules/intake.py — 14-question student intake form.
"""
import streamlit as st

FIELDS = [
    ("name",            "Full Name",                               "text"),
    ("email",           "Email Address",                           "text"),
    ("degree",          "Current / Highest Degree",                "text"),
    ("major",           "Field of Study / Major",                  "text"),
    ("gpa",             "GPA (optional)",                          "text"),
    ("grad_year",       "Graduation Year",                         "number"),
    ("current_role",    "Current Job Title (if any)",              "text"),
    ("years_exp",       "Years of Work Experience",                "number"),
    ("target_role",     "Target Job Role",                         "text"),
    ("target_industry", "Target Industry",                         "text"),
    ("target_location", "Preferred Work Location / Country",       "text"),
    ("remote_pref",     "Remote Preference",                       "select"),
    ("skills_known",    "Skills you already have (comma-separated)","text"),
    ("timeline_months", "Timeline to achieve your goal (months)",  "number"),
]

REQUIRED = {"name","email","degree","major","grad_year","target_role",
            "target_industry","target_location","skills_known","timeline_months"}

def show_intake_form():
    st.subheader("📋 Student Intake Form")
    st.caption("Fill in your details to get a personalised career roadmap.")

    profile = {}
    with st.form("intake"):
        for key, label, ftype in FIELDS:
            if ftype == "text":
                profile[key] = st.text_input(label)
            elif ftype == "number":
                profile[key] = st.number_input(label, min_value=0, max_value=2080, step=1)
            elif ftype == "select":
                profile[key] = st.selectbox(label, ["On-site","Hybrid","Fully Remote"])
        submitted = st.form_submit_button("Save Profile ✅", use_container_width=True)

    if submitted:
        missing = [label for key, label, _ in FIELDS
                   if key in REQUIRED and not str(profile.get(key,"")).strip()]
        if missing:
            st.warning(f"Please fill in: {', '.join(missing)}")
        else:
            st.session_state["profile"] = profile
            st.success("Profile saved! ✅")
            st.rerun()
