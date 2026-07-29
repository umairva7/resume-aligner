# Resume Tailor

**Automatically tailor your resume to any job description using AI.**

Upload your base resume once. Then every time you submit a new job description, get a tailored version that highlights relevant skills and experience—without changing the facts, just the emphasis.

---

## What This Does

### Problem It Solves

Manually rewriting your resume for every job application is:

- Time-consuming (15-30 min per application)
- Error-prone (you might miss key skills the employer wants)
- Inefficient at scale (applying to 50+ jobs?)

### Solution

1. Upload your resume **once** (stores permanently)
2. Upload any job description
3. Get back a tailored resume in **30 seconds** that:
   - Keeps your real experience intact
   - Highlights skills matching the JD
   - Uses keywords the employer is looking for
   - Maintains professional formatting

---

## Tech Stack (Why Each)

| Component | Technology | Why |
| --- | --- | --- |
| **Backend API** | FastAPI (Python) | Fast, clean, built for APIs. You know Python. |
| **LLM** | Use Ollama. | Best at understanding context and rewriting naturally. Better than GPT for nuance. |
| **Storage** | Local filesystem + SQLite | Simple for MVP. No database overhead. Scales fine for 100s of resumes. |
| **Frontend** | HTML + Fetch API | Lightweight, zero dependencies, fast iteration. You can replace with React/Vue later. |
| **Deployment** | Replit/Railway/Vercel | Free tier, instant deploy, no DevOps headaches for MVP. |

**What we *didn't* use:**

- n8n (unnecessary orchestration for 2-endpoint system)
- MongoDB (SQLite is fine for versioning)
- AWS Lambda (Replit/Railway is simpler)
- React (HTML works; add it if you need it later)

**Bottom line:** Minimal tools, maximum functionality. Easy to explain to clients.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Frontend (HTML)                         │
│  ┌──────────────────┐  ┌──────────────────────────────────┐ │
│  │ Upload Base      │  │ Upload Job Description +         │ │
│  │ Resume Form      │  │ Get Tailored Resume Form         │ │
│  └────────┬─────────┘  └──────────────┬───────────────────┘ │
└───────────┼──────────────────────────────┼──────────────────┘
            │                              │
            │ POST /upload-base-resume     │ POST /tailor-resume
            │                              │
┌───────────▼──────────────────────────────▼──────────────────┐
│                    FastAPI Backend                          │
│  ┌──────────────────┐        ┌───────────────────────────┐  │
│  │ Upload Handler   │        │ Resume Tailor Logic       │  │
│  │ (store file)     │        │ (read → prompt → store)   │  │
│  └──────────────────┘        └───────────────────────────┘  │
└──────────────┬─────────────────────────┬────────────────────┘
               │                         │
               │                         │ API call
         ┌─────▼─────┐          ┌────────▼─────────┐
         │  Filesystem │          │  Claude API     │
         │  /uploads/  │          │  (Anthropic)    │
         └─────────────┘          └─────────────────┘
               │
         ┌─────▼──────────────┐
         │ SQLite Database    │
         │ (version history)  │
         └────────────────────┘
```

**Flow:**

1. User uploads base resume → saved to `/uploads/base_resume/`
2. User uploads JD → backend reads both files
3. Backend creates prompt: "Here's a resume + JD, tailor it"
4. Claude rewrites resume to align with JD
5. Tailored version saved to `/uploads/tailored/` with timestamp
6. Versioned in SQLite for audit trail

---

## Installation & Setup

### Prerequisites

- Python 3.9+
- pip (Python package manager)
- Use Ollama.
