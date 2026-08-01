# Resume Aligner Pro 🚀

**Enterprise AI Resume Alignment & ATS Optimization Engine**

Resume Aligner Pro is a high-performance web application designed to analyze match scores between a candidate's base resume and target job descriptions, perform skill gap detection, and dynamically generate ATS-optimized resumes in PDF and Word DOCX formats using modern AI LLM providers.

---

## 🌟 Key Features

1. **Dual Feature Workspace**:
   - **Match Analyzer**: Instant ATS match score calculation, skill breakdown (matched vs missing), keyword density, and strategic recommendation report.
   - **Resume Tailor**: Generates high-impact, ATS-optimized Markdown, PDF, and DOCX resumes aligned with specific job post requirements.
2. **Multi-LLM Strategy Architecture**:
   - **Groq API**: Sub-second cloud inference powered by Llama-3.1-8b (Recommended for production).
   - **Ollama**: Local, private on-premise execution (Llama 3 / Qwen 2.5).
   - **Hugging Face Inference API**: Open-weights serverless inference.
   - **Google Gemini**: High-capacity Google AI inference.
   - **Mock Mode**: Zero-key local testing and demonstration mode.
3. **Performance Caching**:
   - Automatic caching of match analysis reports per base resume to eliminate redundant LLM API calls and optimize latency.
4. **ATS Document Generation**:
   - Professional PDF & DOCX exporters with clean typography, bullet formatting, and clickable social links (LinkedIn, GitHub, Portfolio).
5. **Production Readiness**:
   - Comprehensive `/health` endpoint monitoring Database, Storage, and LLM readiness.
   - Secure HttpOnly session management, input validation, and generic error handlers preventing stack trace leakage.

---

## 🛠️ Tech Stack

- **Backend Framework**: FastAPI (Python 3.9+)
- **Database**: SQLite / SQLAlchemy 2.0 with foreign key enforcement and connection pooling
- **LLM Integration**: HTTPX Async Client supporting Groq, Ollama, Hugging Face, Gemini
- **Document Export**: ReportLab (PDF) & Python-Docx (DOCX)
- **Frontend**: Glassmorphic split-screen HTML5 / Vanilla CSS / Modern JS (No heavy node dependencies)

---

## 🚀 Quick Start (Local Development)

### 1. Clone & Setup Virtual Environment
```bash
git clone https://github.com/umairva7/resume-aligner.git
cd resume-aligner
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure Environment Variables
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```

### 3. Run Development Server
```bash
uvicorn app.main:app --reload --port 8000
```
Open [http://localhost:8000](http://localhost:8000) in your browser.

---

## 🔒 Production Deployment Checklist & Setup

### Deploying to Railway / Render / VPS

1. **Set Environment Variables in Host Dashboard**:
   - `APP_ENV="production"`
   - `DEBUG=False`
   - `SESSION_SECRET="<generate-random-secret>"`
   - `SECURE_COOKIES=True`
   - `ALLOWED_ORIGINS="https://your-domain.up.railway.app"`
   - `LLM_PROVIDER="groq"`
   - `GROQ_API_KEY="<your-groq-api-key>"`

2. **Start Command (via Procfile or CLI)**:
   ```bash
   gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app
   ```

3. **Verify Health Endpoint**:
   Check `https://your-domain.up.railway.app/health` to confirm database, storage, and LLM status.

---

## 🧪 Running Automated Tests

Run the test suite using `pytest`:
```bash
pytest -v
```

---

## 📄 License
MIT License. Created by Umair Imran.
