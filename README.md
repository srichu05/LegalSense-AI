# LegalSense — Context-Aware Legal Document Analysis

LegalSense is a context-aware legal document analysis platform built around **Word Sense Disambiguation (WSD)** using WordNet, lexical relations, and a curated legal glossary. It combines an explainable Python Flask REST backend with a modern, distinctive React + Vite web frontend featuring Three.js 3D lexical network visualizations and GSAP motion design.

---

## Current Status: Reconstructed Phase 3 Completed & Verified

- **Phase 1 (Core WSD Engine):** Complete (WordNet, Extended Lesk, Legal Glossary, uncertainty handling).
- **Phase 2 (Document Intelligence & Flask REST API):** Complete (TXT/PDF ingestion, segmentation, TF-IDF retrieval, REST endpoints with CORS).
- **Phase 3 (React + Vite Web Frontend Reconstruction):** Complete & Verified (Migrated from JavaFX to React + Vite, Tailwind CSS v4, Three.js 3D lexical graph, GSAP transitions, TanStack Query, React Router; 17 Vitest tests passing).
- **Phase 4 (Evaluation, Hardening & Deployment):** Hardened (149 Python backend tests passing, 17 frontend Vitest tests passing, 166 tests total; WSD & retrieval evaluation scripts verified; Render web service & static site ready).
- **Final Academic Project Report:** [`docs/FINAL_PROJECT_REPORT.md`](file:///c:/Users/R%20Raghavendra/Downloads/PROJECTS/LegalSense-AI/docs/FINAL_PROJECT_REPORT.md)

---

## Key Capabilities

1. **Word Sense Disambiguation Engine:**
   - WordNet candidate synsets, definitions, usage examples, and lexical relations (hypernyms, hyponyms, synonyms).
   - Extended Lesk algorithm with weighted gloss, example, and relation overlap scoring.
   - Deterministic tie-breaking, configurable uncertainty thresholds, and itemized token overlap evidence.
   - Sourced legal glossary (10 curated terms) cleanly separated from general WordNet senses.

2. **Distinctive 3D Lexical-Network Visualization (Three.js):**
   - Interactive 3D orbital network graphing real API candidate synsets, hypernyms, hyponyms, and synonyms.
   - Gold-brass central target node with synset spheres, raycasted node inspection, auto-rotation toggle, and camera controls.
   - Fully accessible 2D table fallback available on demand and automatic fallback when WebGL is unavailable.

3. **Document Ingestion & Validation:**
   - Ingestion of `.txt` and `.pdf` files (via PyMuPDF).
   - In-memory processing without persistent storage of uploads.
   - Enforces configurable upload limits (default 5 MB via `LEGAL_SENSE_MAX_UPLOAD_MB`).
   - Page-by-page extraction with page metadata retention and graceful handling of scanned PDFs.

4. **Passage Segmentation & Occurrence Viewer:**
   - Sentence-boundary respecting segmentation into deterministic, coherent passages.
   - Page number and character offset metadata preservation.
   - Structured master-detail occurrence viewer with term search and passage filtering.

5. **Lightweight Document Retrieval:**
   - Combination of TF-IDF cosine similarity (`scikit-learn`), lexical query term matching, and legal glossary boosting.
   - Explainable scoring components (`score_method: "tfidf_lexical_wsd"`).
   - Bundled default legal corpus (`data/sample_documents/`).

6. **Flask REST API:**
   - `GET /health` — Service health and readiness.
   - `POST /api/v1/analyze` — Single-text WSD with explicit or auto-detected target terms.
   - `POST /api/v1/documents/analyze` — Multipart file upload (`.txt` or `.pdf`) with passage-level WSD.
   - `POST /api/v1/search` — Passage search over indexed corpus with ranked results.
   - Full CORS preflight and allowed origins support (`LEGAL_SENSE_CORS_ORIGIN`).

7. **Optional Groq LLM Contextual Assistance:**
   - Configured via server-side `GROQ_API_KEY` (never exposed to frontend/clients).
   - Strict candidate validation: rejects hallucinated synsets and preserves local WSD results.
   - Automatic graceful fallback on timeouts, rate limits, or missing keys.

---

## Quickstart & Installation

### 1. Backend Setup & Startup
```powershell
# Clone or navigate to the repository
cd LegalSense-AI

# Create virtual environment and activate
python -m venv venv
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Download required NLP resources (WordNet, punkt, tagger, stopwords)
python scripts/setup_nlp_resources.py

# Start the Flask API on http://127.0.0.1:5000
python wsgi.py
```

### 2. Frontend Setup & Startup (React + Vite)
In a separate terminal:
```powershell
# Navigate to the frontend directory
cd frontend

# Install npm packages
npm install

# Start local Vite development server (port 5173 with API proxy to port 5000)
npm run dev
```
Open your browser to `http://localhost:5173` to access the LegalSense application.

---

## Testing & Quality Verification

```powershell
# Run Python backend test suite (149 tests passing)
pytest -v

# Run Frontend Vitest suite (17 tests passing)
cd frontend
npm test

# Verify Frontend production build
npm run build
```

---

## Evaluation Benchmarks

```powershell
# Run WSD benchmark (compares MFS baseline vs LegalSense Extended Lesk)
python scripts/evaluate_wsd.py

# Run passage retrieval benchmark (compares TF-IDF vs compound ranking)
python scripts/evaluate_retrieval.py
```

---

## Frontend Architecture

The active frontend is a React + Vite single-page application located in `frontend/`:
- **Design System:** Classical legal editorial palette (Ink Navy `#0f172a`, Warm Ivory `#faf9f5`, Antique Amber `#d97706`).
- **Pages:**
  - **Overview (`/`):** System architecture, real backend health indicator, benchmark statistics, workflow shortcuts.
  - **Text Analysis (`/text-analysis`):** Input clause, target word, Extended Lesk candidates, token overlap evidence, separate legal glossary card, Three.js 3D lexical network.
  - **Document Analysis (`/document-analysis`):** Drag-and-drop `.txt` / `.pdf` ingestion, upload size check, passage occurrence browser with search filtering.
  - **Corpus Search (`/search`):** Compound TF-IDF + lexical ranking, top-k slider, explainable retrieval scores.
  - **Settings (`/settings`):** Backend base URL configuration, ping health check test, diagnostic details.

---

## API Endpoints Summary

| Endpoint | Method | Format | Description |
|---|---|---|---|
| `/health` | `GET` | JSON | Service health, WordNet readiness, LLM flag |
| `/api/v1/analyze` | `POST` | JSON | Analyze text and disambiguate target words |
| `/api/v1/documents/analyze` | `POST` | Multipart | Extract, segment, and disambiguate TXT/PDF |
| `/api/v1/search` | `POST` | JSON | TF-IDF + lexical + WSD passage search |

---

## Documentation Map

| File | Purpose |
|---|---|
| `docs/PRD.md` | Product requirements, users, scope, acceptance criteria (updated for React/Vite) |
| `docs/ARCHITECTURE.md` | Components, data flow, React + Vite frontend, Flask backend |
| `docs/TECH_STACK.md` | Approved technologies and rationale (React, Vite, Tailwind v4, Three.js, GSAP) |
| `docs/PHASE_PLAN.md` | Four-phase implementation sequence and reconstructed Phase 3 status |
| `docs/WSD_DESIGN.md` | WordNet, Extended Lesk, legal glossary, and uncertainty handling |
| `docs/API_SPEC.md` | Flask endpoints, request/response contracts, and error formats |
| `docs/FRONTEND_SPEC.md` | React routes, components, design system, Three.js 3D visualization, and interactions |
| `docs/DATA_AND_EVALUATION.md` | Corpus approach, annotation, metrics, and evaluation protocol |
| `docs/DEPLOYMENT.md` | Render static site (Vite) and web service (Flask) deployment guides |
| `docs/TEST_PLAN.md` | Test strategy: 149 Python tests + 17 Vitest frontend tests |
| `docs/SECURITY_AND_PRIVACY.md` | Secret handling, upload limits, CORS origin configuration, browser data |
| `docs/DECISIONS.md` | Architecture decisions: React + Vite migration, JavaFX retirement, Three.js |
| `docs/ANTIGRAVITY_WORKFLOW.md` | Phase discipline and execution guidelines |
| `docs/PHASE_PROMPTS.md` | Phase master prompts and reconstructed Phase 3 prompt |
| `docs/FINAL_PROJECT_REPORT.md` | Final project report structure and evaluation metrics |
