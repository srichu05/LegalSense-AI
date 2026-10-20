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

## Phase 3 — JavaFX frontend and integration [COMPLETED & VERIFIED]
**Objective:** Deliver a desktop UI that uses the actual backend API.

Tasks:
1. Build a JavaFX application with Home, Text Analysis, Document Analysis, Corpus Search, and Settings views. [DONE]
2. Connect via Java `HttpClient` with asynchronous `CompletableFuture` methods and finite timeouts. [DONE]
3. Render target terms, candidate senses, definitions, lexical relations, uncertainty indicators, itemized overlap evidence, and ranked passages. [DONE]
4. Render curated legal glossary entries visually distinct from WordNet senses. [DONE]
5. Add loading indicators, duplicate submission guarding, input validation, timeouts, and user-friendly error banners. [DONE]
6. Make backend base URL configurable with live health verification. [DONE]
7. Add Java test suite covering models, mock HTTP server, error handling, and live API roundtrips (22 tests passed). [DONE]
8. Verify Python backend regression test suite (142 tests passed). [DONE]

Deliverables:
- Runnable JavaFX application (`com.legalsense.Launcher`, `LegalSenseApp.java`).
- Maven project configuration with wrapper (`pom.xml`, `mvnw.cmd`, `mvnw`).
- Dedicated HTTP API client (`com.legalsense.client.ApiClient`).
- Unit and integration tests (22 tests passing).

Gate: User can submit text from JavaFX and inspect results returned by Flask. [PASSED]

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
