# LegalSense — Security, Privacy and Responsible Use

## 1. Document Handling & Ephemeral Browser Processing

Legal documents may contain confidential, privileged, or personal information. The LegalSense architecture implements the following data-handling boundaries:

- **Browser File Selection:** The React web frontend utilizes standard HTML5 drag-and-drop and file input controls requiring explicit user action to select documents. The frontend does not autonomously scan local storage or cache document contents in `localStorage` or `sessionStorage`.
- **In-Memory Transmission:** Selected file bytes are packaged in-memory as RFC 7578 multipart form data (`FormData`) and streamed over the browser's `fetch` API.
- **No Backend Disk Retention:** Uploaded documents (`POST /api/v1/documents/analyze`) are parsed directly from memory or in-memory byte streams (`io.BytesIO`) during the HTTP request lifecycle. No uploaded document contents are written permanently to disk or retained across requests.
- **Ephemeral Host Safety:** Render's free filesystem is treated as ephemeral. The application does not rely on local file persistence for user data.
- **Demo Corpus:** For development, testing, and demonstrations, only openly licensed or synthetic sample documents (`data/sample_documents/`) are bundled.

## 2. API Secrets & Client Boundary

- **Server-Side Exclusivity:** `GROQ_API_KEY` is loaded exclusively from server-side environment variables on the Flask backend.
- **No Client Secrets:** The React web frontend contains, requests, stores, or logs zero backend secrets, database passwords, or Groq API keys. Only the public API base URL (`VITE_API_BASE_URL`) is exposed to the browser.
- **No Wire Exposure:** The API key is **never** accepted from frontend requests, query parameters, or client headers, and is never returned in API responses or health checks.
- **Placeholder Safety:** `.env.example` in both root and `frontend/` contains only non-secret placeholders.

## 3. CORS & Network Boundaries

- **Configurable Backend CORS:** Flask handles CORS headers via `@app.after_request` and preflight `OPTIONS` routing, enforcing the allowed origin specified by `LEGAL_SENSE_CORS_ORIGIN` (defaults to `*` for local development, and should be restricted to the static site domain in production).
- **Client-Side Pre-Validation:** The React frontend validates file extensions (`.txt` and `.pdf`) and enforces client-side size limits (5 MB) before sending network requests, preventing unnecessary network saturation.
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

## 6. Verification & Client Fault Tolerance Results

Automated regression and hardening suites verified that:
1. **Secret Isolation:** Even when `GROQ_API_KEY` is populated in the environment, zero bytes of the key appear in `/health`, `/api/v1/analyze`, or any error message.
2. **Payload Robustness:** Malformed JSON strings and non-object JSON bodies (e.g. array payloads) are intercepted cleanly and return standard 400 Bad Request error envelopes (`MALFORMED_JSON` / `INVALID_BODY`) without crashing or logging stack traces.
3. **Upload Boundary Enforcement:** Zero-byte uploads, empty filenames, unsupported MIME types, and oversized payloads are rejected at the boundary with appropriate 400/413/415 status codes.
4. **Transient Storage:** Ingestion executes entirely via in-memory byte buffers (`io.BytesIO`), leaving zero residual files in temporary directories or working storage.
5. **Client Fault Tolerance:** The React web frontend uses `AbortController` timeouts (5s health, 30s analysis/search, 60s document upload), guarded duplicate-submission states, and safe non-destructive error banners.

