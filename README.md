# LegalSense — Context-Aware Legal Document Analysis

LegalSense is a context-aware legal document analysis prototype built around **Word Sense Disambiguation (WSD)** using WordNet and lexical relations. It combines an explainable Python backend with a JavaFX desktop frontend and optional Groq-hosted contextual assistance.

---

## Current Status: Phase 4 Completed & Verified (All Phases 1–4 Complete)

- **Phase 1 (Core WSD Engine):** Complete (WordNet, Extended Lesk, Legal Glossary).
- **Phase 2 (Document Intelligence & Flask REST API):** Complete (TXT/PDF ingestion, segmentation, TF-IDF retrieval, REST endpoints).
- **Phase 3 (JavaFX Desktop Client):** Complete (22 Java tests passed, live integration verified).
- **Phase 4 (Evaluation, Hardening & Deployment):** Complete (149 Python tests, 22 Java tests, 171 tests total; WSD & retrieval evaluation scripts verified; Render deployment ready).
- **Final Academic Project Report:** [`docs/FINAL_PROJECT_REPORT.md`](file:///c:/Users/R%20Raghavendra/Downloads/PROJECTS/LegalSense-AI/docs/FINAL_PROJECT_REPORT.md)


---

## Key Capabilities (Phase 1 & 2)

1. **Word Sense Disambiguation Engine:**
   - WordNet candidate synsets, definitions, usage examples, and lexical relations (hypernyms, hyponyms).
   - Extended Lesk algorithm with weighted gloss, example, and relation overlap scoring.
   - Deterministic tie-breaking, configurable uncertainty thresholds, and itemized token overlap evidence.
   - Sourced legal glossary (10 curated terms) cleanly separated from general WordNet senses.

2. **Document Ingestion & Validation:**
   - Ingestion of `.txt` and `.pdf` files (via PyMuPDF).
   - In-memory processing without persistent storage of uploads.
   - Enforces configurable upload limits (default 5 MB via `LEGAL_SENSE_MAX_UPLOAD_MB`).
   - Page-by-page extraction with page metadata retention and graceful handling of scanned PDFs.

3. **Passage Segmentation:**
   - Sentence-boundary respecting segmentation into deterministic, coherent passages.
   - Page number and character offset metadata preservation.

4. **Lightweight Document Retrieval:**
   - Combination of TF-IDF cosine similarity (`scikit-learn`), lexical query term matching, and legal glossary boosting.
   - Explainable scoring components (`score_method: "tfidf_lexical_wsd"`).
   - Bundled default legal corpus (`data/sample_documents/`).

5. **Flask REST API:**
   - `GET /health` — Service health and readiness.
   - `POST /api/v1/analyze` — Single-text WSD with explicit or auto-detected target terms.
   - `POST /api/v1/documents/analyze` — Multipart file upload (`.txt` or `.pdf`) with passage-level WSD.
   - `POST /api/v1/search` — Passage search over indexed corpus with ranked results.

6. **Optional Groq LLM Contextual Assistance:**
   - Configured via server-side `GROQ_API_KEY` (never exposed to frontend/clients).
   - Strict candidate validation: rejects hallucinated synsets and preserves local WSD results.
   - Automatic graceful fallback on timeouts, rate limits, or missing keys.

---

## Quickstart & Installation

### 1. Environment Setup
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
```

### 2. Run Backend & Frontend Tests
```powershell
# Run Python backend test suite (149 tests)
pytest -v

# Run JavaFX client test suite (22 unit & integration tests)
.\mvnw.cmd test
```

### 3. Run Evaluation Benchmarks
```powershell
# Run WSD benchmark (compares MFS baseline vs LegalSense Extended Lesk)
python scripts/evaluate_wsd.py

# Run passage retrieval benchmark (compares TF-IDF vs compound ranking)
python scripts/evaluate_retrieval.py
```

### 4. Start the Flask API
```powershell
# Local development server (port 5000)
python wsgi.py


# Or via Gunicorn (production / Render)
gunicorn wsgi:app
```
The API starts on `http://127.0.0.1:5000` (or the port specified by `$env:PORT`).

### 4. Launch the JavaFX Desktop Client
```powershell
# Launch via Maven wrapper
.\mvnw.cmd javafx:run

# Or via exec plugin
.\mvnw.cmd exec:java
```
The desktop application opens with 5 integrated functional views:
- **Home / Overview:** System purpose, live backend connectivity status, and direct tool entry points.
- **Text Analysis:** Interactive WSD with WordNet synsets, Lesk scores, lexical relations, and curated legal glossary cards.
- **Document Analysis:** Native file picker for `.txt` and `.pdf` files, in-memory processing, passage segmentation, and term occurrence inspection.
- **Corpus Search:** TF-IDF and lexical passage retrieval with score explainability.
- **Settings:** Configurable backend base URL with live health verification.

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
| `docs/PRD.md` | Product requirements, users, scope, requirements, acceptance criteria |
| `docs/ARCHITECTURE.md` | Components, data flow, deployment architecture, design constraints |
| `docs/TECH_STACK.md` | Approved technologies and rationale |
| `docs/PHASE_PLAN.md` | Four-phase implementation sequence and completion gates |
| `docs/WSD_DESIGN.md` | WordNet, Extended Lesk, legal glossary, and uncertainty handling |
| `docs/API_SPEC.md` | Flask endpoints, request/response contracts, and error formats |
| `docs/FRONTEND_SPEC.md` | JavaFX screens, interaction, and integration rules |
| `docs/DATA_AND_EVALUATION.md` | Corpus approach, annotation, metrics, and evaluation protocol |
| `docs/DEPLOYMENT.md` | Render deployment, environment variables, operational limits |
| `docs/TEST_PLAN.md` | Unit, integration, UI, and deployment test strategy |
| `docs/SECURITY_AND_PRIVACY.md` | Secret handling, upload limits, and document privacy |
| `docs/DECISIONS.md` | Recorded architecture and implementation decisions |
| `docs/ANTIGRAVITY_WORKFLOW.md` | Phase discipline and execution guidelines |
| `docs/PHASE_PROMPTS.md` | Phase master prompts and progress tracker |
| `docs/REPORT_TEMPLATE.md` | Final project report structure |
