# LegalSense — Technology Stack

## Approved stack

| Layer | Technology | Actual Version Pin | Purpose | Required on Render? |
|---|---|---|---|---|
| Frontend Web App | React | `react` 19.2.0, `react-dom` 19.2.0 | Core UI components & state | Static host |
| Frontend Bundler | Vite | `vite` 8.3.4 | Development server, HMR, production build | Build time |
| Frontend Styling | Tailwind CSS v4 | `tailwindcss` 4.2.2, `@tailwindcss/vite` 4.2.2 | Utility-first styling & legal editorial design tokens | Build time |
| Frontend Routing | React Router | `react-router-dom` 7.14.0 | Single-page application client routing | Static host |
| API Query / State | TanStack Query | `@tanstack/react-query` 5.95.2 | Asynchronous request lifecycle & status cache | Browser |
| 3D Visualization | Three.js | `three` 0.186.0 | Interactive 3D orbital lexical network graph | Browser |
| Motion / Animation | GSAP | `gsap` 3.15.2 | Selective entrance & candidate focus animations | Browser |
| Icons | Lucide React | `lucide-react` 1.16.0 | Semantic interface icons | Browser |
| Frontend Testing | Vitest + RTL | `vitest` 5.0.5, `@testing-library/react` 16.3.2 | Component, workflow, and API client testing | Development |
| Backend | Python + Flask | `flask>=3.0,<4.0` (3.1.3) | REST endpoints, CORS, and orchestration | Yes |
| WSGI Server | Gunicorn | `gunicorn>=21.0,<24.0` (26.2.0) | Production WSGI runner for Render | Yes |
| Lexical resource | NLTK WordNet | `nltk>=3.8,<4.0` (3.10.3) | Synsets and lexical relations | Yes |
| Preprocessing | spaCy (with NLTK fallback) | `spacy>=3.6,<4.0` (3.8.7) | Tokenization, POS, and lemmatization | Yes |
| WSD baseline | Extended Lesk | Custom engine | Contextual sense scoring | Yes |
| Legal glossary | Versioned JSON | `data/legal_glossary.json` | Curated legal definitions | Yes |
| Document parsing | PyMuPDF | `PyMuPDF>=1.24.0,<1.25.0` (1.24.14) | PDF page-level text extraction | Yes |
| Retrieval | scikit-learn TF-IDF | `scikit-learn>=1.3,<2.0` (1.9.1) | Lightweight passage ranking | Yes |
| Test framework | pytest | `pytest>=7.0,<10.0` (9.1.1) | Backend test suite runner | Development |
| Hosted LLM | Groq API | HTTP REST (urllib) | Optional contextual assistance | No local model |
| Deployment | Render Web Service & Static Site | Python 3.13 / Node 22 | Host Flask API & Vite static bundle | Yes |

## Retired Stack (Phase 3 JavaFX Superseded)

- OpenJDK 21 LTS / JavaFX 21.0.2 desktop client has been completely retired and replaced by the React + Vite web frontend (`frontend/`).
- Maven 3.9.6 wrapper, JUnit 5, and Java HttpClient are removed from the active repository.

## Dependency policy

- Kept minimal and compatible with Render free web service and static site hosting limits.
- No PyTorch, no HuggingFace Transformers, no heavy local neural embedding models.
- PyMuPDF pinned to `1.24.x` to preserve lightweight binary footprint without unnecessary ML dependencies.
- No database, Redis, or cloud object storage needed for the prototype.
- Frontend uses standard JavaScript/JSX, Vite, Tailwind CSS v4, customized shadcn/ui components, GSAP, and Three.js for interactive lexical visualization with 2D accessible fallback.

## Configuration variables

- `GROQ_API_KEY`: optional secret; absent means LLM assistance is disabled.
- `GROQ_MODEL`: optional model identifier (default: `llama-3.3-70b-versatile`).
- `PORT`: server listening port provided by platform (default: 5000).
- `LEGAL_SENSE_MAX_UPLOAD_MB`: upload size limit (default: 5 MB).
- `LEGAL_SENSE_ENABLE_LLM`: feature flag for LLM assistance (default: false or disabled without key).
- `LEGAL_SENSE_CORS_ORIGIN`: CORS allowed origins for backend (default: `*` for local development).
- `VITE_API_BASE_URL`: frontend environment variable for backend URL (default: empty for Vite proxy, or configured to backend Render URL).
