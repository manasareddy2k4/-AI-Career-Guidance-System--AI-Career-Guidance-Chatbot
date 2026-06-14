"""
frontend/app.py — Streamlit UI
Layout: Sidebar | Center Chat | Right Panel
Run: streamlit run frontend/app.py
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import streamlit as st
from config import LANGUAGES
from frontend.modules.api_client   import (send_chat, run_gap_analysis,
                                            get_panel_content, get_job_links,
                                            check_health)
from frontend.modules.intake        import show_intake_form
from frontend.modules.resume_parser import show_resume_parser

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AI Career Guidance System",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Session state defaults ────────────────────────────────────────────────────
for key, default in [
    ("messages",    []),
    ("profile",     {}),
    ("gap_results", {}),
    ("right_panel", {}),
    ("language",    "English"),
]:
    if key not in st.session_state:
        st.session_state[key] = default

WELCOME = """Hi! I'm your **AI Career Co-Pilot** 🚀

I can help you plan a career in **any field** — tech, finance, medicine, law, design, business, and more.

- 🎯 Career paths & timelines
- 📚 Skills to learn & how
- 🧠 Interview preparation guides
- 💼 Job search & salary tips
- 🌐 Works in 17 languages!

Fill the **Intake Form** in the sidebar to get your personalised roadmap,
or just ask me anything right now! 😊"""

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.title("🚀 AI Career Guidance System")

    # API health indicator
    if check_health():
        st.success("🟢 API Connected", icon="✅")
    else:
        st.error("🔴 API Offline — run backend first")
        st.code("uvicorn backend.api:app --reload --port 8000")

    st.divider()

    # Language selector
    lang_names = list(LANGUAGES.keys())
    selected   = st.selectbox(
        "🌐 Language",
        lang_names,
        index=lang_names.index(st.session_state["language"]),
    )
    if selected != st.session_state["language"]:
        st.session_state["language"] = selected
        st.rerun()

    st.divider()

    step = st.radio(
        "Navigation",
        ["💬 Chat", "📋 Step 1: Intake", "📄 Step 2: Resume"],
        label_visibility="collapsed",
    )

    # Job links — shown after profile filled
    profile = st.session_state.get("profile", {})
    if profile.get("target_role"):
        st.divider()
        st.markdown("**🔗 Quick Job Search**")
        role     = profile.get("target_role", "")
        location = profile.get("target_location", "")
        result   = get_job_links(role, location)
        if result:
            st.link_button("💼 LinkedIn", result["linkedin"], use_container_width=True)
            if result.get("naukri"):
                st.link_button("🔍 Naukri", result["naukri"], use_container_width=True)

    st.divider()
    st.caption("Powered by Groq + LLaMA 3")

# ── Layout: chat | right panel ────────────────────────────────────────────────
right_panel = st.session_state.get("right_panel", {})
if right_panel:
    col_chat, col_panel = st.columns([1.1, 0.9])
else:
    col_chat  = st.container()
    col_panel = None

# ── CENTER ────────────────────────────────────────────────────────────────────
with col_chat:

    if step == "💬 Chat":
        st.markdown("### 💬 AI-Career Guidance Sytem")

        # Welcome message
        if not st.session_state["messages"]:
            with st.chat_message("assistant"):
                st.markdown(WELCOME)

        # Chat history
        for msg in st.session_state["messages"]:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        # Input
        user_input = st.chat_input("Ask me anything about your career...")
        if user_input:
            with st.chat_message("user"):
                st.markdown(user_input)

            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    result = send_chat(
                        message  = user_input,
                        history  = st.session_state["messages"],
                        profile  = st.session_state.get("profile", {}),
                        gap      = st.session_state.get("gap_results", {}),
                        language = st.session_state["language"],
                    )

                if result:
                    reply      = result.get("reply", "")
                    panel_type = result.get("panel_type")

                    st.markdown(reply)

                    st.session_state["messages"].append({"role": "user",      "content": user_input})
                    st.session_state["messages"].append({"role": "assistant", "content": reply})

                    # Fetch right panel content if triggered
                    if panel_type:
                        with st.spinner("Loading details..."):
                            p = st.session_state.get("profile", {})
                            if panel_type == "job_links":
                                links = get_job_links(
                                    p.get("target_role",""),
                                    p.get("target_location",""),
                                )
                                if links:
                                    html = f"""<div style='font-family:sans-serif'>
                                    <p><strong>Role:</strong> {p.get('target_role','')} in {p.get('target_location','')}</p>
                                    <a href='{links["linkedin"]}' target='_blank'
                                       style='display:block;padding:12px;background:#0A66C2;color:white;
                                              border-radius:8px;text-decoration:none;text-align:center;
                                              font-weight:bold;margin-bottom:10px'>
                                       💼 Search on LinkedIn</a>"""
                                    if links.get("naukri"):
                                        html += f"""<a href='{links["naukri"]}' target='_blank'
                                           style='display:block;padding:12px;background:#4A90D9;color:white;
                                                  border-radius:8px;text-decoration:none;text-align:center;
                                                  font-weight:bold'>
                                           🔍 Search on Naukri</a>"""
                                    html += "</div>"
                                    st.session_state["right_panel"] = {
                                        "type": "html", "content": html, "title": "🔗 Job Search Links"
                                    }
                            else:
                                panel = get_panel_content(
                                    panel_type = panel_type,
                                    role       = p.get("target_role",""),
                                    skills     = p.get("skills_known",""),
                                    language   = st.session_state["language"],
                                )
                                if panel:
                                    st.session_state["right_panel"] = {
                                        "type":    "markdown",
                                        "content": panel["content"],
                                        "title":   panel["title"],
                                    }
                        st.rerun()

    elif step == "📋 Step 1: Intake":
        show_intake_form()

    elif step == "📄 Step 2: Resume":
        show_resume_parser()
        # Auto-run gap analysis after resume parsed
        p = st.session_state.get("profile", {})
        if p.get("resume_skills") and not st.session_state.get("gap_results"):
            with st.spinner("⚙️ Running gap analysis in background..."):
                gap = run_gap_analysis(
                    target_role   = p.get("target_role",""),
                    skills_known  = p.get("skills_known",""),
                    resume_skills = p.get("resume_skills",[]),
                )
                if gap:
                    st.session_state["gap_results"] = gap
                    st.success("✅ Gap analysis complete!")

    elif step == "📥 Step 3: Report":
        st.subheader("📥 Download Career Report")
        p   = st.session_state.get("profile", {})
        gap = st.session_state.get("gap_results", {})

        if not p:
            st.warning("Complete the Intake Form first.")
        else:
            st.info(
                f"**Student:** {p.get('name','?')}  |  "
                f"**Target:** {p.get('target_role','?')}  |  "
                f"**Gap Analysis:** {'✅ Ready' if gap else '⚠️ Not run yet'}"
            )
            if st.button("Generate PDF Report 📄", use_container_width=True):
                with st.spinner("Building report..."):
                    try:
                        pdf_bytes = build_pdf(p, gap)
                        name      = p.get("name","student").replace(" ","_")
                        st.success(f"✅ Ready! ({len(pdf_bytes):,} bytes)")
                        st.download_button(
                            "⬇️ Download PDF",
                            data      = pdf_bytes,
                            file_name = f"career_roadmap_{name}.pdf",
                            mime      = "application/pdf",
                            use_container_width=True,
                        )
                    except Exception as e:
                        st.error(f"Error: {e}")

# ── RIGHT PANEL ───────────────────────────────────────────────────────────────
if right_panel and col_panel:
    with col_panel:
        st.markdown(f"### {right_panel.get('title','📋 Details')}")
        st.divider()
        if right_panel.get("type") == "html":
            st.components.v1.html(right_panel["content"], height=320, scrolling=True)
        elif right_panel.get("type") == "markdown":
            st.markdown(right_panel["content"])
        st.divider()
        if st.button("✖ Close", use_container_width=True):
            st.session_state["right_panel"] = {}
            st.rerun()
