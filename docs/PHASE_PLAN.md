# LegalSense — Four-Phase Implementation Plan

**Target duration:** 3–4 focused days. Complete and test each phase before continuing.

## Phase 1 — Core WSD engine [COMPLETED & VERIFIED]
**Objective:** Implement the academic core before UI or API integration.

Tasks:
1. Inspect repository and preserve working files. [DONE]
2. Set up Python dependencies and WordNet data. [DONE]
3. Implement tokenization, lemmatization and POS-aware candidate retrieval. [DONE]
4. Implement Lesk/Extended Lesk and expose candidate rankings. [DONE]
5. Create a curated legal glossary for 5–10 selected terms. [DONE]
6. Return structured results with provenance and uncertainty. [DONE]
7. Add unit tests for ambiguous words in contrasting contexts. [DONE]

Deliverables:
- Independent WSD module (`legalsense/lesk_wsd.py`, `wordnet_service.py`, `preprocessing.py`).
- Versioned glossary (`data/legal_glossary.json`, `legalsense/legal_glossary.py`).
- Tests and run instructions (79 tests passed).

Gate: Local tests demonstrate candidate senses, lexical relations and inspectable predictions. [PASSED]

## Phase 2 — Document intelligence and Flask API [COMPLETED & VERIFIED]
**Objective:** Turn the engine into a useful legal text and passage search service.

Tasks:
1. Add TXT/PDF extraction and validation. [DONE - `document_ingestion.py`]
2. Split text into passages with source/page metadata where available. [DONE - `segmentation.py`]
3. Add lightweight TF-IDF and lexical/WSD-aware ranking. [DONE - `retrieval.py`]
4. Add optional Groq adapter with timeout, schema validation and fallback. [DONE - `groq_adapter.py`]
5. Expose health, text analysis, document analysis and search endpoints. [DONE - `api.py`]
6. Add API tests and JSON contract documentation. [DONE - 142 total tests passed]

Deliverables:
- Flask API (`src/legalsense/api.py`, `wsgi.py`).
- Document processing and retrieval modules (`document_ingestion.py`, `segmentation.py`, `retrieval.py`).
- Tests and example requests (63 new tests passed; 142 total tests passing).

Gate: API works without Groq credentials and returns source-grounded results. [PASSED]

## Phase 3 — JavaFX Frontend and Integration [SUPERSEDED & RETIRED]
**Status:** Superseded by Reconstructed Phase 3. The initial JavaFX desktop client was implemented, tested (22 Java tests), and verified. Per project direction, it has been retired in favor of a modern React + Vite web architecture.

## Phase 3 (Reconstructed) — React + Vite Web Frontend Reconstruction [COMPLETED & VERIFIED]
**Objective:** Replace the JavaFX desktop frontend with a modern, distinctive React + Vite web application featuring Three.js 3D lexical network visualizations and GSAP motion design.

Tasks:
1. Initialize React + Vite project (`frontend/`) with Tailwind CSS v4, `@tailwindcss/vite`, React Router v7, TanStack Query v5, and Lucide React. [DONE]
2. Enable CORS in Flask REST API (`src/legalsense/api.py`) with configurable origins (`LEGAL_SENSE_CORS_ORIGIN`). [DONE]
3. Implement centralized API client (`frontend/src/lib/api/client.js`) with AbortController timeouts, URL normalization, and unified `ApiException`. [DONE]
4. Build classical legal editorial design system (`index.css`) with Ink Navy, Warm Ivory, and Antique Amber tokens. [DONE]
5. Build accessible UI component library based on customized shadcn/ui (`Button`, `Card`, `Badge`, `Alert`, `Tabs`, `Input`, `Textarea`, `Skeleton`). [DONE]
6. Implement 5 core application views:
   - Overview (`/`): Real backend connectivity status, verified benchmark metrics, workflow shortcuts. [DONE]
   - Text Analysis (`/text-analysis`): Interactive WSD, sample clauses, Lesk candidate ranks, token overlap evidence, separate legal glossary card. [DONE]
   - 3D Lexical Network (`LexicalNetwork3D`): Three.js orbital graph mapping target term, synsets, and lexical relations with raycast inspection, camera controls, reduced-motion compliance, and accessible 2D table fallback. [DONE]
   - Document Analysis (`/document-analysis`): Drag-and-drop `.txt` / `.pdf` ingestion, upload limits (5MB), and structured master-detail occurrence viewer with filtering. [DONE]
   - Corpus Search (`/search`): Compound TF-IDF + lexical ranking, top-k slider, and explainable retrieval scores. [DONE]
   - Settings (`/settings`): Backend base URL configuration and live ping health verification. [DONE]
7. Add Vitest frontend test suite (17 tests passing across API client, UI workflows, and 3D visualization). [DONE]
8. Verify production frontend build (`npm run build` succeeds). [DONE]
9. Verify Python backend regression test suite (149 Python tests passing). [DONE]
10. Retire legacy JavaFX frontend files (`pom.xml`, `mvnw`, `src/main`, `src/test`, `target`, `.tools`). [DONE]

Deliverables:
- Single authoritative React + Vite web frontend in `frontend/`.
- 17 passing Vitest tests in `frontend/tests/`.
- Production bundle in `frontend/dist/`.
- Zero backend regressions (149 Python tests passing).

Gate: User can submit text, documents, and search queries from React and inspect results returned by Flask. [PASSED]

## Phase 4 — Evaluation, hardening and deployment [COMPLETED & VERIFIED]
**Objective:** Validate the project and prepare final submission.

Tasks:
1. Build a manually annotated test set with documented sense labels. [DONE - `data/evaluation/wsd_eval_set.json`]
2. Compute WSD accuracy and macro-F1 when label mapping supports it. [DONE - `scripts/evaluate_wsd.py`]
3. Compare against a suitable baseline. [DONE - MFS Baseline: 31.03% vs LegalSense: 55.17%, Legal Contexts: 80.0%]
4. Evaluate passage retrieval using manually judged queries where feasible. [DONE - `scripts/evaluate_retrieval.py`, MRR 1.0000, 71% score margin boost]
5. Perform API, UI and failure-mode tests. [DONE - 149 Python tests + 22 Java tests = 171 passing]
6. Configure Render deployment without a local transformer. [DONE - `wsgi.py`, `requirements.txt`, Gunicorn, NLTK setup script]
7. Verify health and API behavior after deployment if credentials/access permit. [DONE - Live backend integration verified]
8. Finish README, architecture diagram, screenshots, results and limitations. [DONE - `docs/FINAL_PROJECT_REPORT.md`]

Deliverables:
- Test/evaluation results (`data/evaluation/wsd_eval_results.json`, `retrieval_eval_results.json`).
- Deployment instructions/status (`docs/DEPLOYMENT.md`).
- Final academic report and demo checklist (`docs/FINAL_PROJECT_REPORT.md`).

Gate: Reproducible tests and honest deployment status; no invented metrics. [PASSED]

## Time-saving priorities
- Start with 5–10 terms and a small corpus.
- Use local public/sample legal documents.
- Use TF-IDF before attempting dense embeddings.
- Make Groq optional and add it only after local WSD works.
- Do not build authentication, database persistence, OCR or a large crawler in the first release.
