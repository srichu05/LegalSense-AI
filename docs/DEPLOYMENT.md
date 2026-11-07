# LegalSense — Deployment & Hosting Guide

## 1. Deployment Architecture

LegalSense consists of two independently deployable components:
1. **Backend Web Service:** The lightweight Python Flask REST API running on Render via Gunicorn.
2. **Frontend Static Site:** The React + Vite single-page application built to static HTML/CSS/JS (`frontend/dist/`) and hosted on Render Static Sites, Vercel, or Netlify.

No transformer models or heavy weights are downloaded or loaded on Render. Groq LLM inference is remote and entirely optional.

---

## 2. Pre-Deployment Verification Status

- [x] Local Flask API runs (`wsgi.py` on port 5000).
- [x] All 149 Python unit and API tests pass (`pytest -v`).
- [x] All 17 frontend Vitest tests pass (`cd frontend && npm test`).
- [x] Frontend builds cleanly (`cd frontend && npm run build` producing `frontend/dist/`).
- [x] `requirements.txt` contains pinned, compatible packages with lightweight PyMuPDF 1.24.x and Gunicorn.
- [x] WordNet data installation is reproducible via `scripts/setup_nlp_resources.py`.
- [x] Zero transformer weights required.
- [x] `GET /health` responds with HTTP 200 and readiness status.
- [x] Full CORS preflight and headers supported via `LEGAL_SENSE_CORS_ORIGIN`.
- [x] Groq is optional; core WSD, ingestion, and search function with `GROQ_API_KEY` absent.
- [x] Upload limits (default 5 MB) and timeouts (6.0s) enforced.
- [x] Backend binds to platform `$PORT` via `wsgi.py`.
- [x] Uploaded files are processed in-memory without persistent disk dependence.

---

## 3. Component A: Flask API (Render Web Service)

### Service Configuration
- **Type:** Web Service
- **Runtime:** `Python 3.13`
- **Build Command:**
  ```bash
  pip install -r requirements.txt && python scripts/setup_nlp_resources.py
  ```
- **Start Command:**
  ```bash
  gunicorn wsgi:app
  ```

### Environment Variables
| Variable | Required? | Default / Purpose |
|---|---|---|
| `PORT` | Auto-set by Render | Port the WSGI server binds to |
| `LEGAL_SENSE_CORS_ORIGIN` | No | Allowed frontend domain (e.g. `https://legalsense.onrender.com` or `*`) |
| `LEGAL_SENSE_MAX_UPLOAD_MB` | No | `5` (Maximum document upload size in MB) |
| `LEGAL_SENSE_ENABLE_LLM` | No | `false` (Enable/disable Groq LLM assistance) |
| `GROQ_API_KEY` | No | Optional API key for remote LLM assistance |
| `GROQ_MODEL` | No | `llama-3.3-70b-versatile` |

---

## 4. Component B: React + Vite Frontend (Render Static Site / Vercel)

### Static Site Configuration
- **Type:** Static Site
- **Runtime:** `Node 20+` / `Node 22`
- **Root Directory:** `frontend` (or project root with directory set to `frontend`)
- **Build Command:**
  ```bash
  npm install && npm run build
  ```
- **Publish Directory:** `dist` (relative to `frontend/`, i.e., `frontend/dist`)
- **SPA Routing Rule (Render Redirects/Rewrites):**
  - Source: `/*`
  - Destination: `/index.html`
  - Action: `Rewrite`

### Environment Variables
| Variable | Required? | Default / Purpose |
|---|---|---|
| `VITE_API_BASE_URL` | No | URL of deployed Flask backend (e.g. `https://legalsense-api.onrender.com`). If empty, uses Vite's relative `/api` proxy. |

---

## 5. Local Development Startup

### Terminal 1: Python Flask Backend
```powershell
# Navigate to project root
cd LegalSense-AI

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Run Flask WSGI server
python wsgi.py
```
Backend runs on `http://127.0.0.1:5000`.

### Terminal 2: React + Vite Frontend
```powershell
# Navigate to frontend directory
cd LegalSense-AI\frontend

# Install dependencies if not already installed
npm install

# Start Vite dev server
npm run dev
```
Frontend runs on `http://localhost:5173` with automatic API proxying to `http://127.0.0.1:5000`.

---

## 6. Verification Steps (Post-Deployment)

1. `GET https://<api-url>/health` -> verify `"status": "ok"`, `"wsd_ready": true`.
2. Open `https://<frontend-url>/` -> check that the live backend status pill shows "Backend Online".
3. Navigate to **Text Analysis** -> submit test clause "Consideration must be of some value in the eye of the law" for target word "consideration" -> verify WordNet synsets, token evidence, legal glossary card, and 3D lexical network.
4. Navigate to **Document Analysis** -> upload `data/sample_documents/sample_contract.txt` -> verify passage occurrence extraction.
5. Navigate to **Corpus Search** -> submit query "consideration contract" -> verify ranked passages.
6. Verify graceful fallback if `GROQ_API_KEY` is not configured.

