# LegalSense — Antigravity Phase Master Prompts

Use one prompt at a time. Complete its acceptance criteria and verify the phase before moving to the next. These prompts are also summarized in `docs/PHASE_PLAN.md`.

## Phase 1 — Core WSD engine [COMPLETED & VERIFIED]

> Implement LegalSense Phase 1 in the existing repository. Read `README.md`, `docs/PRD.md`, `docs/WSD_DESIGN.md`, `docs/TECH_STACK.md`, `docs/TEST_PLAN.md` and `docs/ANTIGRAVITY_WORKFLOW.md` first. Inspect the existing code and preserve working functionality. Set up Python, NLTK WordNet and spaCy as needed. Implement preprocessing, POS-aware WordNet candidate retrieval, gloss/example/lexical-relation extraction, and a documented Lesk or Extended Lesk baseline. Add a small sourced legal glossary with provenance, distinct from WordNet. Return structured candidate rankings, evidence and uncertainty. Add tests for contrasting contexts, ties, unknown words and missing relations. Do not build the frontend, API or deployment in this phase. Run tests and report actual outcomes, commands, changed files and unresolved issues.

*Status:* **Completed**. 79 unit tests passed. WordNet service, Extended Lesk, legal glossary, and data schemas verified.

---

## Phase 2 — Document intelligence and Flask API [COMPLETED & VERIFIED]

> Implement LegalSense Phase 2. Read `docs/PRD.md`, `docs/ARCHITECTURE.md`, `docs/API_SPEC.md`, `docs/SECURITY_AND_PRIVACY.md`, `docs/DEPLOYMENT.md` and `docs/ANTIGRAVITY_WORKFLOW.md`. Reuse the Phase 1 WSD engine. Add TXT/PDF extraction, passage segmentation with source/page metadata, lightweight TF-IDF and lexical/WSD-aware passage ranking, and a Flask REST API matching `docs/API_SPEC.md`. Add optional server-side Groq integration using `GROQ_API_KEY`, strict output validation and timeouts. The backend must work without a Groq key and fall back to local results on provider errors. Add request validation, upload limits, safe error responses and API tests. Do not build the JavaFX UI or load transformer weights. Run tests and report actual outcomes and remaining issues.

*Status:* **Completed**. 142 total tests passed (79 Phase 1 + 63 Phase 2). Ingestion (`document_ingestion.py`), segmentation (`segmentation.py`), retrieval (`retrieval.py`), Groq adapter (`groq_adapter.py`), and Flask API (`api.py` / `wsgi.py`) verified live.

---

## Phase 3 — JavaFX frontend [COMPLETED & VERIFIED]

> Implement LegalSense Phase 3. Read `docs/FRONTEND_SPEC.md`, `docs/API_SPEC.md`, `docs/ARCHITECTURE.md` and `docs/ANTIGRAVITY_WORKFLOW.md`. Build a professional JavaFX desktop client that uses Java `HttpClient` and the actual Flask API schema. Include text analysis, TXT/PDF selection, corpus search, candidate senses, lexical relations, source provenance, uncertainty and ranked passage display. Keep the backend URL configurable, run network requests off the UI thread, add timeouts/loading/error states, and never embed the Groq key in Java. Preserve the Python WSD logic in the backend. Build and run the UI, test integration against the API, and report actual results.

*Status:* **Completed**. 22 Java tests passed (10 mock server + 8 JSON models + 4 live backend integration tests). JavaFX application built with OpenJDK 21 LTS, JavaFX 21.0.2, and Apache Maven 3.9.6 wrapper. All 5 views implemented and verified live against Flask backend. 142 Python regression tests passing.

---

## Phase 4 — Evaluation, deployment and final submission [COMPLETED & VERIFIED]

> Implement LegalSense Phase 4. Read `docs/DATA_AND_EVALUATION.md`, `docs/DEPLOYMENT.md`, `docs/TEST_PLAN.md`, `docs/SECURITY_AND_PRIVACY.md`, `docs/REPORT_TEMPLATE.md` and `docs/ANTIGRAVITY_WORKFLOW.md`. Audit the full repository, create a documented manually annotated WSD evaluation set, calculate real metrics, compare with an appropriate baseline, and perform error analysis. Test search relevance where feasible. Prepare a lightweight Render deployment without transformer models, ensure WordNet data is reproducibly available, keep Groq optional, and verify health/analyze/search endpoints if deployment access is available. Finish the README, report, architecture and demo instructions. Do not fabricate metrics or claim unverified deployment success. Report exact tests, actual results, deployment status and limitations.

*Status:* **Completed**. 149 Python tests and 22 Java tests passed (171 tests total). WSD evaluation benchmark executed (MFS baseline 31.03% vs LegalSense 55.17%, legal domain 80.0%, confident selective accuracy 92.31%). Stopword filtering implemented and regression tested. Retrieval benchmark executed (MRR 1.0000, 71% score margin boost, negative query rejection). Render deployment configuration verified with Gunicorn and automated NLTK setup. Final academic project report generated in `docs/FINAL_PROJECT_REPORT.md`.

