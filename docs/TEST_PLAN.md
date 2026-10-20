# LegalSense — Test Plan & Execution Results

## 1. Test Suite Overview

LegalSense features a comprehensive two-tier automated testing strategy covering both the Python NLP/REST backend and the JavaFX desktop integration client:

- **Python Backend Test Runner:** `pytest 9.1.1`
  - **Status:** **149 passed, 0 failed, 0 skipped** (Execution time: ~25s)
  - **Configuration:** `pytest.ini` (`pythonpath = src`, `testpaths = tests`)
- **Java Desktop Test Runner:** `Maven Surefire 3.2.5` with `JUnit 5.10.2`
  - **Status:** **22 passed, 0 failed, 0 skipped** (Execution time: ~11s against live backend)
  - **Build Command:** `.\mvnw.cmd test`
- **Total Automated Test Count:** **171 tests passed across all tiers**

---

## 2. Java Desktop Client Test Coverage (22 Tests)

### ApiClient Unit & Mock Server Tests (`com.legalsense.client.ApiClientTest` — 10 tests)
- **Base URL Sanitization:** Handles trailing slashes, whitespace, and resets to default `http://127.0.0.1:5000`.
- **Health Check (`GET /health`):** Verifies parsing of status, service name, `wsd_ready`, and `llm_enabled`.
- **Text Analysis (`POST /api/v1/analyze`):** Validates full payload roundtrip via local mock server, checking candidate senses, Extended Lesk scores, lexical relations (synonyms, hypernyms), and legal glossary entries.
- **Client Input Validation:** Verifies immediate client-side rejection of empty or blank text without dispatching network calls.
- **Error Response Handling:** Validates parsing of structured backend error payloads (`code` and `message`) into typed `ApiException`.
- **Document Upload (`POST /api/v1/documents/analyze`):** Validates RFC 7578 multipart formatting with file byte stream, filename, content type, and `use_llm` form fields.
- **Document Input Validation:** Rejects non-existent paths, unsupported file types (e.g. `.docx`), and empty (0-byte) files.
- **Corpus Search (`POST /api/v1/search`):** Validates search query serialization and hit extraction (document name, page, score, matched terms).
- **Search Input Validation:** Rejects empty or whitespace search queries.
- **Network Failure & Timeouts:** Tests connection failure against unreachable endpoints, verifying human-readable messages without stack traces.

### JSON Resilient Serialization Tests (`com.legalsense.model.JsonModelTest` — 8 tests)
- **Forward Compatibility:** Verifies that unknown server fields are safely ignored (`FAIL_ON_UNKNOWN_PROPERTIES=false`).
- **Request Serialization:** Validates JSON serialization of `AnalyzeRequest` and `SearchRequest`.
- **Missing Optional Fields:** Verifies safe parsing when optional fields (`selected_sense`, `evidence`, `warnings`, `page`, `legal_glossary_entry`) are omitted or null.
- **Lexical Relations:** Tests parsing of synonyms, hypernyms, and hyponyms lists.
- **Glossary Details:** Tests parsing of legal jurisdiction, source provenance, examples, and limitations.
- **Document Response:** Validates extraction of page counts, character counts, and passage occurrences.
- **Corpus Search Response:** Validates hit ranking, score methods, and matched term arrays.
- **Error Envelope:** Tests parsing of standard API error responses (`error.code`, `error.message`).

### Live Backend End-to-End Tests (`com.legalsense.client.LiveBackendIntegrationTest` — 4 tests)
- **Live Health Check:** Verifies `/health` on live Flask backend at `http://127.0.0.1:5000`.
- **Live Text Analysis:** Submits legal text and target term "consideration", verifying that actual WordNet synsets, Lesk scores, and legal glossary entries are returned.
- **Live Document Upload:** Sends bundled `sample_contract.txt` via multipart upload, verifying live extraction, passage segmentation, and term occurrence detection.
- **Live Corpus Search:** Executes real TF-IDF search query "consideration contract mutual promises" against indexed legal corpus.
*(Note: These live integration tests automatically execute whenever the local Flask server is running on port 5000, and gracefully skip via JUnit Assumptions if the server is offline).*

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
