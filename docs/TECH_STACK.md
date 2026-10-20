# LegalSense — Technology Stack

## Approved stack

| Layer | Technology | Actual Version Pin | Purpose | Required on Render? |
|---|---|---|---|---|
| Desktop UI | Java + JavaFX | OpenJDK 21 LTS / JavaFX 21.0.2 | Native user interface (Phase 3) | No |
| Desktop Build | Apache Maven | Maven 3.9.6 (via Maven Wrapper `mvnw`) | Dependency management & compilation | No |
| HTTP client | Java `HttpClient` | `java.net.http.HttpClient` (JDK 21) | Asynchronous API communication | No |
| JSON Parser | Jackson | `jackson-databind` 2.17.0 | Resilient JSON (de)serialization | No |
| Desktop Testing | JUnit 5 | `junit-jupiter` 5.10.2 | Unit & mock server test runner | Development |
| Backend | Python + Flask | `flask>=3.0,<4.0` (3.1.3) | REST endpoints and orchestration | Yes |
| WSGI Server | Gunicorn | `gunicorn>=21.0,<24.0` (26.2.0) | Production WSGI runner for Render | Yes |
| Lexical resource | NLTK WordNet | `nltk>=3.8,<4.0` (3.10.3) | Synsets and lexical relations | Yes |
| Preprocessing | spaCy (with NLTK fallback) | `spacy>=3.6,<4.0` (3.8.7) | Tokenization, POS, and lemmatization | Yes |
| WSD baseline | Extended Lesk | Custom engine | Contextual sense scoring | Yes |
| Legal glossary | Versioned JSON | `data/legal_glossary.json` | Curated legal definitions | Yes |
| Document parsing | PyMuPDF | `PyMuPDF>=1.24.0,<1.25.0` (1.24.14) | PDF page-level text extraction | Yes |
| Retrieval | scikit-learn TF-IDF | `scikit-learn>=1.3,<2.0` (1.9.1) | Lightweight passage ranking | Yes |
| Test framework | pytest | `pytest>=7.0,<10.0` (9.1.1) | Test suite runner | Development |
| Hosted LLM | Groq API | HTTP REST (urllib) | Optional contextual assistance | No local model |
| Deployment | Render web service | Python 3.13 Web Service | Host Flask API | Yes |

## Dependency policy

- Kept minimal and compatible with Render free web service limits.
- No PyTorch, no HuggingFace Transformers, no heavy local embedding models.
- PyMuPDF pinned to `1.24.x` to preserve lightweight binary footprint without unnecessary ML dependencies.
- No database, Redis, or cloud object storage needed for the prototype.
- Java desktop client relies solely on OpenJDK 21, JavaFX 21 controls, and Jackson, keeping the desktop build standalone and reproducible via the included `mvnw` wrapper.

## Configuration variables

- `GROQ_API_KEY`: optional secret; absent means LLM assistance is disabled.
- `GROQ_MODEL`: optional model identifier (default: `llama-3.3-70b-versatile`).
- `PORT`: server listening port provided by platform (default: 5000).
- `LEGAL_SENSE_MAX_UPLOAD_MB`: upload size limit (default: 5 MB).
- `LEGAL_SENSE_ENABLE_LLM`: feature flag for LLM assistance (default: false or disabled without key).
- `LEGALSENSE_API_URL`: optional client-side environment override for backend URL (default: `http://127.0.0.1:5000`).
