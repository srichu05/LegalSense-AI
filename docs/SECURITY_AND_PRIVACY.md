# LegalSense — Security, Privacy and Responsible Use

## 1. Document Handling & Ephemeral Processing

Legal documents may contain confidential, privileged, or personal information. The LegalSense architecture implements the following data-handling boundaries:

- **Client File Selection:** The JavaFX client uses the native OS `FileChooser` (`javafx.stage.FileChooser`) requiring explicit user interaction to select files. The client does not scan local directories autonomously or persist uploaded files locally.
- **In-Memory Transmission:** Selected file bytes are streamed directly via HTTP multipart form data over Java's `HttpClient`.
- **No Backend Disk Retention:** Uploaded documents (`POST /api/v1/documents/analyze`) are parsed directly from memory or in-memory streams (`io.BytesIO`) during the HTTP request lifecycle. No uploaded document contents are written permanently to disk or retained across requests.
- **Ephemeral Host Safety:** Render's free filesystem is treated as ephemeral. The application does not rely on local file persistence for user data.
- **Demo Corpus:** For development, testing, and demonstrations, only openly licensed or synthetic sample documents (`data/sample_documents/`) are bundled.

## 2. API Secrets & Client Boundary

- **Server-Side Exclusivity:** `GROQ_API_KEY` is loaded exclusively from server-side environment variables on the Flask backend.
- **No Client Secrets:** The Java desktop client does not contain, request, store, or log `GROQ_API_KEY` or any backend credentials. The client Settings view allows configuring only the backend base URL.
- **No Wire Exposure:** The API key is **never** accepted from frontend requests, query parameters, or client headers, and is never returned in API responses or health checks.
- **Placeholder Safety:** `.env.example` contains only empty placeholder strings.

## 3. Input Validation & Resource Limits

- **Client-Side Pre-Validation:** The desktop client checks file extensions (`.txt` and `.pdf`), verifies file existence, and checks for non-zero file sizes before initiating network upload.
- **Upload Size Limits:** Enforced via `MAX_CONTENT_LENGTH` in Flask and `LEGAL_SENSE_MAX_UPLOAD_MB` (default: 5 MB). Excessively large files are rejected immediately with HTTP 413.
- **Text Length Limits:** Single-text analysis (`POST /api/v1/analyze`) is capped at 50,000 characters.
- **Filename Sanitization:** All uploaded filenames pass through `sanitize_filename()`, which strips path traversal sequences (`../`, `..\\`) and control characters, preventing directory traversal vulnerabilities.
- **Internal Document Identifiers:** Random safe slugs (`doc_<uuid>`) are assigned internally to avoid exposing filesystem paths.
- **Safe Error Handling:** Unhandled exceptions return sanitized JSON errors (`{"error": {"code": "INTERNAL_SERVER_ERROR", "message": "..."}}`). Raw Python tracebacks and internal file paths are never exposed to clients or rendered in the UI.

## 4. LLM Safety Controls

When optional Groq contextual assistance is enabled:
- Only the sentence containing the target word and the candidate WordNet definitions are sent to the external API; full documents are never forwarded.
- The model is restricted to a structured JSON schema requiring selection only among existing candidate synsets or explicit abstention (`NONE`).
- The backend validates the response against the candidate set; any hallucinated synsets or invalid identifiers are discarded, preserving the local WSD prediction.
- Timeouts (6.0 seconds) and connection error handlers ensure the system falls back gracefully to local WSD without interrupting service.

## 5. Legal-Use Disclaimer

LegalSense is an educational and research prototype for lexical analysis and document navigation. It does not provide legal advice, determine rights or obligations, or replace review by a qualified legal professional. WordNet is a general English lexical database, not an authoritative legal ontology.

## 6. Phase 4 Verification & Hardening Results

Automated regression and hardening suites (`tests/test_api.py::TestApiHardeningAndSecurity`, `ApiClientTest`, and `LiveBackendIntegrationTest`) verified that:
1. **Secret Isolation:** Even when `GROQ_API_KEY` is populated in the environment, zero bytes of the key appear in `/health`, `/api/v1/analyze`, or any error message.
2. **Payload Robustness:** Malformed JSON strings and non-object JSON bodies (e.g. array payloads) are intercepted cleanly and return standard 400 Bad Request error envelopes (`MALFORMED_JSON` / `INVALID_BODY`) without crashing or logging stack traces.
3. **Upload Boundary Enforcement:** Zero-byte uploads, empty filenames, unsupported MIME types, and oversized payloads are rejected at the boundary with appropriate 400/413/415 status codes.
4. **Transient Storage:** Ingestion executes entirely via in-memory byte buffers (`io.BytesIO`), leaving zero residual files in temporary directories or working storage.
5. **Client Fault Tolerance:** The Java desktop client enforces a 10-second timeout on live analysis and a 5-second timeout on health checks, preventing UI thread freezing or duplicate submission race conditions.

