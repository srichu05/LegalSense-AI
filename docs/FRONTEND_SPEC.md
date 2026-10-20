# LegalSense — JavaFX Frontend Specification

## 1. Design Objective

Build a clean, robust Java desktop application for legal text exploration and Word Sense Disambiguation (WSD). The UI makes WSD evidence transparent, separates general WordNet senses from curated legal definitions, and clearly communicates that the system is an academic research tool rather than an authoritative legal advisor.

## 2. Implemented Architecture & Views

The application is structured into five primary views managed by `MainLayout` with dynamic view switching:

### A. Home / Overview (`HomeView.java`)
- **Title and Description:** Displays LegalSense purpose, technical overview (WordNet + Extended Lesk + Legal Glossary), and system principles.
- **Backend Connection Card:** Shows currently configured endpoint, live health status pill, and actions to refresh connection or configure settings.
- **Direct Workspace Cards:** Direct entry buttons to Text Analysis, Document Analysis, and Corpus Search.
- **Scope & Principles:** Explains transparent scoring evidence, uncertainty flags, and separation of knowledge sources.
- **Constraint Compliance:** No fabricated usage statistics or artificial accuracy metrics.

### B. Text Analysis (`TextAnalysisView.java`)
- **Inputs:**
  - Multiline text area for legal text/clauses (up to 50,000 characters).
  - Target word field (optional; if left blank, backend auto-detects candidate terms).
  - Checkbox for optional Groq LLM assistance.
  - Sample clause buttons ("Contract Consideration", "Motion Excerpt", "Instrument Execution") for rapid demonstration.
- **Actions:** "Run Analysis" (disables inputs during processing) and "Clear".
- **Results Display:**
  - Summary bar with analyzed term count and request ID.
  - Uncertainty indicator (`badge-uncertain`) when score ties or weak overlap are detected.
  - Visually distinct legal glossary card (`legal-glossary-card` in amber) showing term, jurisdiction, definition, usage example, source, and educational limitations.
  - Ranked WordNet candidate senses table/cards with synset ID, score, definition, rank, and lexical relations (synonyms, hypernyms, hyponyms).
  - Selected sense badge (`badge-selected`).
  - Itemized token overlap evidence panel.
  - LLM assistance status panel (suggested sense and model rationale).

### C. Document Analysis (`DocumentAnalysisView.java`)
- **File Chooser:** Native `javafx.stage.FileChooser` supporting `.txt` and `.pdf` documents.
- **Validation:** Enforces file existence, size checks, and extension filtering prior to transmission.
- **Sample Document Shortcuts:** One-click loading of bundled sample documents (`sample_contract.txt`, `sample_court_ruling.txt`).
- **Metadata Card:** Displays Document ID, filename, format, character count, page count, and passage count.
- **Warnings Banner:** Prominently alerts the user when text extraction produces warnings (e.g. scanned PDFs or empty pages).
- **Occurrences Table:** Master-detail view of all detected legal terms across document passages, including page number and selected sense.
- **Detail Panel:** Selecting any occurrence renders full `SenseDetailCard` analysis.

### D. Corpus Search (`CorpusSearchView.java`)
- **Query Input:** Search field for natural language legal queries.
- **Sample Queries:** Quick-fill buttons for contract consideration, motions to dismiss, and confidentiality obligations.
- **Result Count Selector:** Spinner for `top_k` (1 to 20, default 5).
- **Passage Cards:** Displays ranked passages with document name, page number (if available), retrieval score (`tfidf_lexical_wsd`), and matched terms.
- **Interpretability Notice:** Explains that retrieval scores are ranking signals rather than probabilities of legal validity.

### E. Settings & Connection Status (`SettingsView.java`)
- **Configuration:** Base URL configuration field (default: `http://127.0.0.1:5000`).
- **Connection Test:** Tests live backend health via `GET /health` with millisecond latency reporting.
- **Status Reporting:** Inspects service name, WordNet readiness, and Groq LLM activation flag.
- **Security Boundary:** Explicitly notes that backend credentials (such as `GROQ_API_KEY`) remain strictly on the backend and are never stored or exposed in the desktop client.

## 3. Visual & Aesthetic Standards

- **Restrained Palette:**
  - Primary Slate/Navy: `#0F172A`, `#1E293B`
  - Crisp Background: `#F8FAFC`
  - Cards & Surfaces: `#FFFFFF` with subtle `#E2E8F0` borders
  - Legal Glossary Accent: Amber/gold `#FCD34D` / `#FEF3C7` / `#92400E` (ensures visual distinction from general WordNet definitions)
  - WordNet Accent: Blue `#EFF6FF` / `#1D4ED8`
  - Uncertainty Alert: Orange `#FFF7ED` / `#C2410C`
- **Typography:** Modern clean system typography (`Segoe UI`, `Roboto`, `Helvetica Neue`, sans-serif) with clear hierarchy and readable line-spacing.
- **Disclaimer Banner:** Persistent banner pinned at the bottom of the window: *"⚖ LegalSense is an academic legal NLP research tool. It does not provide legal advice or authoritative interpretations."*

## 4. Technical Integration & Threading Rules

- **HTTP Client:** Java's standard `java.net.http.HttpClient` with finite timeouts (5s connect, 30s request).
- **Asynchronous Execution:** All API interactions (`checkHealth`, `analyzeText`, `analyzeDocument`, `searchCorpus`) return `CompletableFuture`.
- **UI Thread Safety:** All UI updates are marshaled back to the JavaFX Application Thread via `Platform.runLater()`.
- **Duplicate Prevention:** Action buttons are disabled and loading spinners are activated during in-flight network requests.
- **JSON Processing:** Jackson (`jackson-databind` 2.17.0) configured with `FAIL_ON_UNKNOWN_PROPERTIES=false` for resilient deserialization.
- **Error Handling:** Typed `ApiException` unwraps backend error envelopes (`INVALID_REQUEST`, `FILE_TOO_LARGE`, `UNSUPPORTED_FORMAT`, etc.) and presents clean, user-friendly messages without stack traces.

## 5. Known Limitations

- **No OCR:** Image-only or scanned PDFs are flagged with warnings; no OCR is performed in Phase 3.
- **Session-Only Uploads:** Uploaded documents are processed in-memory for the duration of the request and are not stored in a persistent corpus.
- **Desktop Only:** Runs as a native desktop application; no browser or web frontend.
