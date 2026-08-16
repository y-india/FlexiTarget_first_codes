from __future__ import annotations

import base64
import io
import os
import re
from typing import Any

import requests
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from openai import OpenAI
from pypdf import PdfReader
from docx import Document
from docx.shared import Pt

try:
    from PIL import Image
    import pytesseract
except Exception:
    Image = None
    pytesseract = None

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "").strip()
OPENROUTER_MODEL = os.getenv(
    "OPENROUTER_MODEL",
    "nvidia/nemotron-3-ultra-550b-a55b:free",
).strip()
GOOGLE_APPS_SCRIPT_WEB_APP_URL = os.getenv("GOOGLE_APPS_SCRIPT_WEB_APP_URL", "").strip()
MAX_TEXT_CHARS = int(os.getenv("MAX_TEXT_CHARS", "50000"))

app = FastAPI(title="ResumeRefresh Processing API", version="2.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"] ,
    allow_headers=["*"] ,
)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(_: Request, exc: RequestValidationError):
    messages = []
    for item in exc.errors():
        loc = ".".join(str(x) for x in item.get("loc", []))
        messages.append(f"{loc}: {item.get('msg', 'Invalid value')}")
    return JSONResponse(status_code=422, content={"ok": False, "error": "; ".join(messages)})


@app.exception_handler(Exception)
async def unhandled_exception_handler(_: Request, exc: Exception):
    # Always return JSON so the Chrome extension can display the real failure.
    return JSONResponse(status_code=500, content={"ok": False, "error": str(exc) or "Unexpected backend error."})


class ResumePayload(BaseModel):
    name: str
    mimeType: str = "application/octet-stream"
    size: int = 0
    base64: str


class ProcessRequest(BaseModel):
    userId: str
    name: str
    gmail: str
    jobDescription: str = Field(min_length=20)
    resume: ResumePayload


def decode_file(resume: ResumePayload) -> bytes:
    try:
        return base64.b64decode(resume.base64, validate=True)
    except Exception as exc:
        raise ValueError(f"Invalid resume encoding: {exc}")


def extract_resume_text(resume: ResumePayload, data: bytes) -> str:
    filename = resume.name.lower()

    if filename.endswith(".pdf") or resume.mimeType == "application/pdf":
        reader = PdfReader(io.BytesIO(data))
        pages = [(page.extract_text() or "") for page in reader.pages]
        text = "\n\n".join(pages)
    elif filename.endswith(".docx") or "wordprocessingml.document" in resume.mimeType:
        doc = Document(io.BytesIO(data))
        parts = [p.text for p in doc.paragraphs if p.text.strip()]
        for table in doc.tables:
            for row in table.rows:
                parts.append(" | ".join(cell.text.strip() for cell in row.cells))
        text = "\n".join(parts)
    elif filename.endswith((".png", ".jpg", ".jpeg", ".webp")):
        if Image is None or pytesseract is None:
            raise ValueError("Image OCR dependencies are not installed. Use PDF or DOCX, or install Tesseract OCR.")
        text = pytesseract.image_to_string(Image.open(io.BytesIO(data)))
    elif filename.endswith(".doc") or resume.mimeType == "application/msword":
        raise ValueError("Legacy .doc files are not supported by this MVP. Save the resume as .docx or PDF and upload again.")
    else:
        raise ValueError("Supported resume formats are PDF, DOCX, PNG, JPG, and WEBP.")

    text = re.sub(r"\n{3,}", "\n\n", text).strip()
    if not text:
        raise ValueError("No readable text was found in the resume. If it is a scanned PDF, upload a text-based PDF or an image file with OCR enabled.")
    return text[:MAX_TEXT_CHARS]


def get_client() -> OpenAI:
    if not OPENROUTER_API_KEY:
        raise ValueError("OPENROUTER_API_KEY is not configured. Create a backend .env file and restart Uvicorn.")
    return OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=OPENROUTER_API_KEY,
        default_headers={
            "HTTP-Referer": "https://resumerefresh.local",
            "X-Title": "ResumeRefresh",
        },
    )


def extract_model_content(message: Any) -> str:
    content = getattr(message, "content", None)
    if isinstance(content, str):
        return content.strip()
    if isinstance(content, list):
        pieces = []
        for part in content:
            if isinstance(part, dict):
                value = part.get("text") or part.get("content") or ""
            else:
                value = getattr(part, "text", "") or getattr(part, "content", "") or ""
            if value:
                pieces.append(str(value))
        return "\n".join(pieces).strip()
    return str(content or "").strip()


def personalize_resume(job_description: str, resume_text: str):
    client = get_client()
    prompt = f"""
You are the resume personalization engine for ResumeRefresh.

Tailor the candidate's existing resume to the supplied job description.

Strict rules:
1. Never invent employers, degrees, dates, projects, metrics, certifications, tools, achievements, or experience.
2. Preserve factual claims from the original resume unless clearly irrelevant.
3. Reorder and rewrite wording to emphasize skills genuinely present in the original resume.
4. Use ATS terminology from the job description only when the original resume supports it.
5. Do not claim a skill merely because the job description asks for it.
6. Return a complete updated resume in plain text with clear section headings.
7. After the updated resume, write the exact marker ===CHANGES=== and then 3 to 6 short lines explaining what changed and why.

JOB DESCRIPTION:
{job_description[:30000]}

ORIGINAL RESUME:
{resume_text}
"""
    try:
        response = client.chat.completions.create(
            model=OPENROUTER_MODEL,
            messages=[{"role": "user", "content": prompt}],
            extra_body={"reasoning": {"enabled": True}},
        )
    except Exception as exc:
        raise RuntimeError(f"OpenRouter request failed: {exc}")

    message = response.choices[0].message
    content = extract_model_content(message)
    if not content:
        raise RuntimeError("The model returned an empty response.")

    if "===CHANGES===" in content:
        resume_part, changes_part = content.split("===CHANGES===", 1)
    else:
        resume_part, changes_part = content, "The wording and ordering were tailored to the supplied job description."

    resume_part = re.sub(r"^```(?:text|markdown)?\s*", "", resume_part.strip(), flags=re.I)
    resume_part = re.sub(r"\s*```$", "", resume_part.strip())
    return resume_part.strip(), changes_part.strip()


def make_docx_base64(resume_text: str) -> str:
    doc = Document()
    section = doc.sections[0]
    section.top_margin = Pt(36)
    section.bottom_margin = Pt(36)
    section.left_margin = Pt(48)
    section.right_margin = Pt(48)
    for raw_line in resume_text.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        is_heading = bool(re.fullmatch(r"[A-Z][A-Z0-9 &/,+-]{2,55}", line))
        p = doc.add_paragraph()
        r = p.add_run(line)
        r.bold = is_heading
        r.font.size = Pt(12 if is_heading else 10.5)
    output = io.BytesIO()
    doc.save(output)
    return base64.b64encode(output.getvalue()).decode("ascii")


def save_to_google_backend(req: ProcessRequest, original_text: str, personalized: str, changes: str):
    if not GOOGLE_APPS_SCRIPT_WEB_APP_URL:
        raise ValueError("GOOGLE_APPS_SCRIPT_WEB_APP_URL is not configured in the backend .env file.")
    payload = {
        "action": "submit_job",
        "userId": req.userId,
        "name": req.name,
        "gmail": req.gmail,
        "jobDescription": req.jobDescription,
        "originalResumeText": original_text,
        "personalizedResume": personalized,
        "changes": changes,
        "resume": {
            "name": req.resume.name,
            "mimeType": req.resume.mimeType,
            "size": req.resume.size,
            "base64": req.resume.base64,
        },
    }
    try:
        response = requests.post(GOOGLE_APPS_SCRIPT_WEB_APP_URL, json=payload, timeout=120)
    except Exception as exc:
        raise RuntimeError(f"Could not reach Google Apps Script: {exc}")
    raw = response.text
    try:
        data = response.json()
    except Exception:
        raise RuntimeError(f"Google Apps Script returned non-JSON HTTP {response.status_code}: {re.sub(r'\s+', ' ', raw)[:300]}")
    if not response.ok or data.get("ok") is False:
        raise RuntimeError(data.get("error", f"Google Apps Script returned HTTP {response.status_code}"))
    return data


@app.get("/")
def root():
    return {"ok": True, "service": "ResumeRefresh Processing API", "status": "online"}


@app.get("/health")
def health():
    return {
        "ok": True,
        "service": "ResumeRefresh Processing API",
        "model": OPENROUTER_MODEL,
        "openrouterConfigured": bool(OPENROUTER_API_KEY),
        "appsScriptConfigured": bool(GOOGLE_APPS_SCRIPT_WEB_APP_URL),
    }


@app.post("/process")
def process(req: ProcessRequest):
    data = decode_file(req.resume)
    original_text = extract_resume_text(req.resume, data)
    personalized, changes = personalize_resume(req.jobDescription, original_text)
    docx_base64 = make_docx_base64(personalized)
    google_result = save_to_google_backend(req, original_text, personalized, changes)
    safe_name = re.sub(r"[^A-Za-z0-9._-]+", "_", req.name).strip("_") or "Resume"
    return {
        "ok": True,
        "originalResumeText": original_text,
        "personalizedResume": personalized,
        "changes": changes,
        "docxBase64": docx_base64,
        "fileName": f"{safe_name}_ResumeRefresh.docx",
        "saved": bool(google_result.get("saved", google_result.get("ok", False))),
        "resumeDriveUrl": google_result.get("resumeUrl"),
    }
