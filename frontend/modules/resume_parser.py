"""
frontend/modules/resume_parser.py
Extracts text from PDF locally, sends text to API for NER parsing.
"""
import sys, os
import streamlit as st

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from config import TESSERACT_PATH
from frontend.modules.api_client import parse_resume_text

# ── PDF text extraction (local — no API needed) ───────────────────────────────
try:
    import fitz
except ImportError:
    fitz = None

try:
    import pytesseract
    from PIL import Image
    import io
    pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False

def extract_text(pdf_bytes: bytes) -> str:
    text = ""
    if fitz:
        try:
            doc  = fitz.open(stream=pdf_bytes, filetype="pdf")
            text = "\n".join(page.get_text() for page in doc)
            doc.close()
        except Exception:
            text = ""

    # OCR fallback for scanned PDFs
    if not text.strip() and OCR_AVAILABLE and fitz:
        try:
            doc   = fitz.open(stream=pdf_bytes, filetype="pdf")
            parts = []
            for page in doc:
                pix = page.get_pixmap(dpi=300)
                img = Image.open(io.BytesIO(pix.tobytes("png")))
                parts.append(pytesseract.image_to_string(img))
            doc.close()
            text = "\n".join(parts)
        except Exception:
            text = ""
    return text.strip()

def show_resume_parser():
    st.subheader("📄 Resume Parser")
    st.caption("Upload your resume — text or scanned PDF both work.")

    if not st.session_state.get("profile"):
        st.warning("⚠️ Complete the Intake Form first.")
        return

    uploaded = st.file_uploader("Upload Resume (PDF)", type=["pdf"])
    if not uploaded:
        return

    if st.button("Parse Resume 🔍", use_container_width=True):
        with st.spinner("Extracting text from PDF..."):
            pdf_bytes = uploaded.read()
            text      = extract_text(pdf_bytes)

        if not text:
            st.error("Could not extract text. Check Tesseract is installed for scanned PDFs.")
            return

        st.caption(f"✅ Extracted {len(text):,} characters")

        with st.spinner("Sending to API for analysis..."):
            result = parse_resume_text(text)

        if result:
            st.session_state["profile"].update(result)
            st.session_state["profile"]["resume_skills"] = result.get("skills", [])
            st.success("Resume parsed successfully! ✅")
            st.json(result)
