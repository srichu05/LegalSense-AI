# LegalSense — Test Plan & Execution Results

## 1. Test Suite Overview

LegalSense features a comprehensive two-tier automated testing strategy covering both the Python NLP/REST backend and the React + Vite web frontend:

- **Python Backend Test Runner:** `pytest 9.1.1`
  - **Status:** **149 passed, 0 failed, 0 skipped** (Execution time: ~36s)
  - **Configuration:** `pytest.ini` (`pythonpath = src`, `testpaths = tests`)
  - **Execution Command:** `pytest -v`
- **Frontend Web Test Runner:** `Vitest 5.0.5` with `@testing-library/react 16.3.2` & `jsdom`
  - **Status:** **17 passed, 0 failed, 0 skipped** (Execution time: ~10s)
  - **Configuration:** `frontend/vite.config.js` (`test: { environment: 'jsdom' }`)
  - **Execution Command:** `cd frontend && npm test`
- **Total Automated Test Count:** **166 tests passed across all active tiers**
- **Legacy Java Client:** 22 Java tests retired alongside the JavaFX desktop client.

---

## 2. React + Vite Frontend Test Coverage (17 Tests)

### API Client Layer (`frontend/tests/apiClient.test.js` — 8 tests)
- **Base URL Sanitization & Config:** Verifies default `/api` base URL, custom `VITE_API_BASE_URL` handling, and runtime `localStorage` configuration override.
- **Health Check (`GET /health`):** Verifies request dispatch, JSON response unwrapping, and readiness inspection.
- **Text Analysis (`POST /api/v1/analyze`):** Validates request payload serialization with text, target word, and LLM flag.
- **Document Analysis (`POST /api/v1/documents/analyze`):** Validates RFC 7578 multipart file upload serialization with `file` form key and `use_llm` flag.
- **Corpus Search (`POST /api/v1/search`):** Validates query string and `top_k` parameter transmission.
- **Client Input Validation:** Immediately rejects empty or whitespace-only inputs before triggering network calls.
- **Error Response Handling:** Maps non-2xx responses to structured `ApiException` with backend error code and HTTP status code.
- **Network Failure & Timeouts:** Handles connection rejection and `AbortController` timeouts, providing descriptive diagnostic messages.

### UI Workflows & Pages (`frontend/tests/uiWorkflows.test.jsx` — 6 tests)
- **Overview Page:** Validates editorial headline, verified empirical benchmark metrics, and workflow shortcut links.
- **Text Analysis Page:** Verifies that clicking sample clause buttons ("Contract Consideration", "Motion Excerpt", "Instrument Execution") immediately fills the clause and target word inputs.
- **WsdResultCard Presentation:** Asserts strict visual and semantic separation between general WordNet candidate rankings and the curated amber `LegalGlossaryCard`.
- **Uncertainty & Evidence Display:** Verifies display of the uncertainty alert badge when `uncertain=True` and token overlap evidence details.
- **Document Analysis Workspace:** Validates drag-and-drop file upload zone, client-side 5 MB file size limit enforcement, and unsupported extension rejection.
- **Corpus Search Workspace:** Verifies natural language query submission, top-k slider, and `SearchResultCard` score explainability disclaimers.
- **Settings Workspace:** Verifies base URL configuration input and ping test execution against the health endpoint.

### 3D Lexical-Network Visualization (`frontend/tests/visualization.test.jsx` — 3 tests)
- **LexicalNetwork3D Rendering:** Renders Three.js orbital network canvas, target word header, and interactive controls.
- **Accessible 2D Table Fallback:** Verifies that clicking "View 2D Table" toggles the accessible tabular view showing synset IDs, definitions, hypernyms, and hyponyms, and toggles back to 3D WebGL on demand.
- **Graceful Empty State:** Safely renders an informative fallback message when candidate senses are empty without crashing.

---

## 3. Python Backend Test Coverage (142 Tests)

### Preprocessing (`tests/test_preprocessing.py` — 18 tests)
- Empty input, whitespace-only, punctuation-only handling.
- Case preservation in original text vs. lowercased lemmas.
- POS tagging across nouns, verbs, adjectives, and adverbs.
- Target word token identification by lemma and inflected forms.
- Gloss and example tokenization with punctuation stripping.

### WordNet & WSD Engine (`tests/test_wordnet_service.py` & `tests/test_lesk_wsd.py` — 44 tests)
- WordNet synset retrieval, glosses, and usage examples.
- POS-aware filtering (noun, verb, adjective, adverb).
- Lexical relation extraction (hypernyms and hyponyms).
- Extended Lesk weighted overlap scoring and candidate ranking.
- Contrasting contexts producing divergent rankings (`bank` financial vs. river, `suit` legal vs. garment).
- Deterministic scoring and tie-breaking.
- Uncertainty detection for low scores, zero overlap, and ties.
- Itemized token overlap evidence linking candidates to context.
- Phase 4 stopword filtering regression tests (`TestStopwordFiltering`).

### Legal Glossary (`tests/test_legal_glossary.py` — 19 tests)
- JSON parsing and strict schema validation.
- In-memory caching and cache resetting.
- Case-insensitive term lookup.
- Strict isolation of glossary entries from WordNet synsets.
- Verification of default 10 curated legal terms.

### Document Ingestion & Validation (`tests/test_document_ingestion.py` — 11 tests)
- Ingestion from file paths, raw bytes, and file-like streams.
- Supported format validation (`.txt`, `.pdf`).
- Rejection of unsupported extensions (`.docx`, etc.).
- Rejection of empty files (0 bytes) and whitespace-only files.
- Enforcing file upload limits (`max_bytes` / `LEGAL_SENSE_MAX_UPLOAD_MB`).
- Filename sanitization against path traversal.
- Real PyMuPDF page-by-page extraction and page metadata preservation.
- Scanned/image-only PDF detection with warnings.
- Corrupt PDF error handling.

### Passage Segmentation (`tests/test_segmentation.py` — 11 tests)
- Sentence splitting and exact character offset tracking.
- Segmentation respecting sentence boundaries (no mid-sentence truncations).
- Deterministic passage IDs (`doc_<id>_p001`).
- Multi-page document segmentation retaining page numbers per passage.
- Handling empty and whitespace-only sections.

### Lightweight Retrieval (`tests/test_retrieval.py` — 9 tests)
- TF-IDF + lexical + legal glossary boost ranking.
- Handling empty queries, whitespace queries, and empty collections.
- Zero-score and no-match queries.
- `top_k` clamping and deterministic ranking order.
- Output conformance with `docs/API_SPEC.md § 4`.

### Groq LLM Adapter (`tests/test_groq_adapter.py` — 7 tests)
- Disabled state when `GROQ_API_KEY` is absent or `LEGAL_SENSE_ENABLE_LLM` is false.
- Validation of suggested synsets: strict rejection of hallucinated synset IDs not in candidate senses.
- Clean handling of model abstention (`NONE`).
- Network timeouts (`urllib.error.URLError`) and HTTP errors falling back to local WSD without crashing.

### Flask REST API & Hardening (`tests/test_api.py` — 30 tests)
- `GET /health`: 200 OK, returns `wsd_ready` and `llm_enabled`.
- `POST /api/v1/analyze`:
  - Valid requests with explicit target words.
  - Automatic detection of legal terms when `target_word` is omitted.
  - Rejection of non-JSON content types (HTTP 400).
  - Validation of missing, empty, or oversized text (> 50,000 characters).
- `POST /api/v1/documents/analyze`:
  - Valid multipart TXT and PDF uploads.
  - Rejection of missing files and empty filenames (HTTP 400).
  - Rejection of unsupported media types (HTTP 415).
  - Rejection of empty files (HTTP 400).
- `POST /api/v1/search`:
  - Valid search against indexed legal corpus.
  - Rejection of missing or empty queries (HTTP 400).
  - Validation of `top_k` bounds (HTTP 400).
  - Safe empty results array and warning on no-match queries.
- Consistent JSON error response shape across all endpoints.
- Security and hardening (`TestApiHardeningAndSecurity`):
  - Malformed JSON string rejection (`MALFORMED_JSON`).
  - Non-object / array body rejection (`INVALID_BODY`).
  - Strict secret isolation (ensuring `GROQ_API_KEY` is never leaked in payloads, headers, or error strings).
  - Empty filename multipart rejection (`EMPTY_FILENAME`).


---

## 4. Manual Verification Checklist

In addition to automated tests, the following manual GUI checks were performed:
1. **Startup & Views Navigation:** Verified that the JavaFX application initializes, displays `MainLayout`, and navigates smoothly across Home, Text Analysis, Document Analysis, Corpus Search, and Settings.
2. **Backend Status Pill:** Verified that the header pill displays "● Backend Online (WSD Ready)" when Flask is active, and switches to "● Backend Disconnected" when the backend is unreachable.
3. **Sample Clause Loading:** Verified that clicking sample buttons ("Contract Consideration", "Motion Excerpt", "Instrument Execution") populates the text area and target word field correctly.
4. **Glossary Amber Distinction:** Verified that curated legal glossary entries render with distinct amber styling (`.legal-glossary-card`), clearly segregated from WordNet candidate senses.
5. **Score Interpretation Notice:** Verified that Corpus Search explicitly documents that retrieval scores are ranking signals rather than legal validity probabilities.
6. **Disclaimer Banner:** Verified that the legal research disclaimer remains visible across all screens.
