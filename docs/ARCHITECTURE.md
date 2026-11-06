# LegalSense — Architecture

## 1. High-level design

```text
+-------------------------------------------------------------------------------+
|                       React + Vite Web Frontend (`frontend/`)                 |
|                                                                               |
|  [AppShell] <-> [Navbar] with [BackendStatusPill] & [Footer]                  |
|       |                                                                       |
|       +--> [OverviewPage]           (Architecture, real health, benchmarks)  |
|       +--> [TextAnalysisPage]       (Interactive WSD, samples, results)       |
|       |      +--> [WsdResultCard]   (Candidate ranks, Lesk scores, GSAP)     |
|       |      +--> [LexicalNetwork3D](Three.js 3D graph + 2D table fallback)  |
|       |      +--> [LegalGlossaryCard] (Black's Law source-grounded card)      |
|       |      +--> [EvidencePanel]   (Exact token overlaps)                   |
|       +--> [DocumentAnalysisPage]   (Drag-and-drop .txt/.pdf, validation)     |
|       |      +--> [PassageOccurrenceViewer] (Occurrence filter/inspection)   |
|       +--> [CorpusSearchView]       (TF-IDF & lexical query ranking)         |
|       +--> [SettingsPage]           (Base URL configuration & health test)   |
|                                                                               |
|  [client.js] (Fetch API, AbortController timeouts, unified ApiException)      |
|  [TanStack Query] (Asynchronous request lifecycle & status management)       |
|  [Three.js] (WebGL lexical graph visualization with raycasting & 2D fallback) |
|  [GSAP] (Deliberate entry transitions & candidate selection highlighting)     |
+-------------------------------------------------------------------------------+
                                      |
                                      | HTTP REST / JSON / Multipart (CORS)
                                      v
+-------------------------------------------------------------------------------+
|                    Flask REST API (`wsgi.py` / `api.py`)                      |
|                                                                               |
|  GET  /health                      POST /api/v1/analyze                       |
|  POST /api/v1/search               POST /api/v1/documents/analyze             |
|  OPTIONS * (CORS preflight via LEGAL_SENSE_CORS_ORIGIN)                       |
+-------------------------------------------------------------------------------+
        |
        +--> Input validation / orchestration (upload limits, JSON checks)
        |
        +--> Text preprocessing (`src/legalsense/preprocessing.py`)
        |      +--> spaCy tokenization/POS/lemmatization (NLTK fallback)
        |
        +--> WSD engine (`src/legalsense/lesk_wsd.py`)
        |      +--> NLTK WordNet synsets/glosses/relations (`wordnet_service.py`)
        |      +--> Extended Lesk scoring & evidence generation
        |      +--> Curated legal glossary (`legal_glossary.py` / `legal_glossary.json`)
        |
        +--> Document ingestion & validation (`src/legalsense/document_ingestion.py`)
        |      +--> TXT decoding & text normalization
        |      +--> PDF page-by-page extraction via PyMuPDF (fitz)
        |
        +--> Passage segmentation (`src/legalsense/segmentation.py`)
        |      +--> Sentence-boundary respecting chunking
        |      +--> Page number and character offset metadata
        |
        +--> Lightweight retrieval (`src/legalsense/retrieval.py`)
        |      +--> scikit-learn TF-IDF cosine similarity
        |      +--> Lexical query term overlap
        |      +--> Legal glossary domain boost
        |      +--> Bundled sample legal corpus (`data/sample_documents/`)
        |
        +--> Optional Groq adapter (`src/legalsense/groq_adapter.py`)
               (server-side only; strict candidate validation; local fallback)
```

## 2. Component responsibilities & Module Boundaries

### React + Vite Web Client (`frontend/`)
- **Single Authoritative Frontend:** Completely supersedes the legacy JavaFX desktop application.
- **Presentation & Interaction:** Built with React 19, Vite, Tailwind CSS v4, and customized shadcn/ui components (`Button`, `Card`, `Badge`, `Alert`, `Tabs`, `Input`, `Textarea`).
- **Sense Detail Presentation:** Visually distinguishes general WordNet candidate rankings from curated legal definitions (`LegalGlossaryCard`), highlighting lexical relations and exact token overlap evidence (`EvidencePanel`).
- **3D Lexical-Network Visualization (`LexicalNetwork3D`):** Three.js orbital graph mapping target term, synsets, and lexical relations. Includes node raycasting, inspection tooltips, camera controls, reduced-motion compliance, and accessible 2D table fallback.
- **Dedicated HTTP Client (`client.js`):** Built on browser standard `fetch` with `AbortController` timeouts, automatic proxy support in dev (`/api` -> `5000`), custom base URL support, and centralized `ApiException` handling.
- **Secret Separation:** Frontend contains zero backend secrets, database passwords, or Groq API keys. Only public `VITE_API_BASE_URL` is configured.
- **Algorithm Isolation:** JavaScript does not duplicate WSD algorithms or lexical models; all NLP analysis remains authoritative on the Python Flask backend.

### Flask API (`src/legalsense/api.py`)
- Endpoints: `GET /health`, `POST /api/v1/analyze`, `POST /api/v1/documents/analyze`, `POST /api/v1/search`.
- Validate inputs, content types, and request payload bounds.
- Orchestrate preprocessing, WSD, document ingestion, passage segmentation, and retrieval.
- Enforce request size limits (`LEGAL_SENSE_MAX_UPLOAD_MB`) and safe error formatting.

### Document Ingestion (`src/legalsense/document_ingestion.py`)
- Support `.txt` and `.pdf` files.
- PyMuPDF (`fitz`) extracts text page-by-page with 1-indexed page metadata.
- Sanitize filenames to prevent traversal; generate safe internal IDs (`doc_<uuid>`).
- Normalize whitespace and CRLF without breaking sentence boundaries.
- Gracefully detect scanned PDFs with no extractable text.
- Memory/request-scoped processing; no persistent disk retention of uploads.

### Passage Segmentation (`src/legalsense/segmentation.py`)
- Sentence-boundary aware chunking into ~150-word coherent passages.
- Retain `document_id`, `document_name`, `passage_id`, `page`, and character offsets.
- Deterministic output ensuring identical inputs yield identical passage IDs.

### Retrieval Engine (`src/legalsense/retrieval.py`)
- Combines TF-IDF cosine similarity (`TfidfVectorizer`), lexical query term overlap, and legal glossary boosting.
- Explainable scoring components: `score_method: "tfidf_lexical_wsd"`.
- Indexes bundled sample corpus (`data/sample_documents/`) on startup.

### WSD Engine (`src/legalsense/lesk_wsd.py` & `wordnet_service.py`)
- Dynamic NLTK WordNet candidate retrieval and POS filtering.
- Extended Lesk scoring: gloss (1.0), examples (1.0), hypernym gloss (0.5), hyponym gloss (0.5).
- Itemized token overlap evidence (`EvidenceItem`).
- Deterministic tie-breaking and uncertainty estimation (`uncertain=True`).
- Sourced legal glossary integration (`LegalGlossaryEntry`) kept distinct from WordNet.

### Groq Adapter (`src/legalsense/groq_adapter.py`)
- Reads secret from `GROQ_API_KEY`.
- Uses configurable model (`GROQ_MODEL`, default: `llama-3.3-70b-versatile`).
- Applies 6-second network timeout.
- Strict validation: rejects any synset ID not in the WordNet candidate list.
- Graceful fallback to local WSD on failure, rate limit, or absent key.

## 3. Request lifecycle

1. Client submits HTTP request (JSON or multipart file upload).
2. Flask validates request type, length, file format, and required fields.
3. Preprocessor tokenizes and extracts linguistic annotations.
4. Document Ingestion extracts text page-by-page (for file uploads).
5. Segmentation chunks text into sentence-respecting passages.
6. WSD engine scores candidate senses against context and flags uncertainty.
7. Retrieval engine ranks passages using TF-IDF, lexical overlap, and domain boost.
8. If configured and requested, Groq provides an optional contextual suggestion.
9. Backend validates the suggestion and returns the standardized JSON response.

## 4. Deployment topology

- Flask runs as a lightweight web service on Render via `gunicorn wsgi:app` or locally via `python wsgi.py`.
- React + Vite web frontend builds to static HTML/CSS/JS (`frontend/dist/`) and deploys via Render Static Sites, Vercel, or Netlify, proxying/connecting to the Flask backend.
- WordNet data is installed into the Python runtime environment.
- No transformer weights, GPU, or local neural models are required.
- Groq inference is remote and entirely optional.
