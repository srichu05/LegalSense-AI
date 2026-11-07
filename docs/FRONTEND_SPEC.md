# LegalSense — React + Vite Frontend Specification

## 1. Design Objective

Deliver a polished, distinctive web application for legal research and computational linguistics. The UI combines classical legal editorial typography with modern data visualization, making Word Sense Disambiguation (WSD) evidence transparent, separating general WordNet senses from curated legal definitions, providing interactive 3D lexical network exploration, and clearly communicating the tool's educational and research boundaries.

The active frontend is a React + Vite single-page application located in `frontend/`, superseding the legacy JavaFX desktop client.

---

## 2. Design System & Editorial Aesthetics

The application adheres to a restrained, research-oriented legal editorial palette:
- **Ink Navy (`#0f172a`, `#1e293b`):** Primary navigation, structural headers, and deep visual contrast.
- **Warm Parchment / Ivory (`#faf9f5`, `#f8fafc`):** Main working surfaces and card backgrounds.
- **Antique Amber / Brass (`#d97706`, `#b45309`, `#fef3c7`):** Reserved exclusively for Black's Law legal glossary distinctions, highlighting curated domain knowledge.
- **WordNet Slate / Blue (`#2563eb`, `#eff6ff`):** WordNet synset candidate rankings, relations, and algorithmic evidence.
- **Uncertainty Alert (`#ea580c`, `#fff7ed`):** Prominent badges and banners when Extended Lesk detects score ties or low overlap.
- **Editorial Typography:** High-contrast serif headings (`Merriweather`, `Georgia`, serif) paired with crisp sans-serif interface text (`Inter`, system-ui).

---

## 3. Implemented Routes & Workspaces

The application uses React Router v7 with an `AppShell` container, top navigation bar, live `BackendStatusPill`, and persistent educational disclaimer footer.

### A. Overview Workspace (`/`)
- **Product Descriptor:** Clarifies LegalSense's role as a computational linguistics and legal NLP research platform.
- **Live Health Status:** Interactive status card querying `GET /health` with service status, WordNet readiness, and LLM flags.
- **Verified Benchmark Metrics:** Displays empirically verified benchmark results (LegalSense 55.17% overall accuracy, 80.0% legal context accuracy vs 31.03% MFS baseline; MRR 1.0000 on retrieval).
- **Direct Workflow Entry Points:** Actionable shortcut cards directing users to Text Analysis, Document Analysis, and Corpus Search.

### B. Text Analysis Workspace (`/text-analysis`)
- **Inputs:**
  - Multiline text area for legal clauses (up to 50,000 characters).
  - Target word field (optional; auto-detects ambiguous candidate terms when empty).
  - Checkbox for optional Groq LLM contextual assistance.
  - One-click sample clause buttons ("Contract Consideration", "Motion Excerpt", "Instrument Execution").
- **Actions:** "Disambiguate Text" (disables during request to prevent duplicate submissions) and "Clear".
- **Evidence-First Results Presentation:**
  - Request summary with analyzed term count and timestamp.
  - Uncertainty banner when backend reports `uncertain=True` (score ties or weak context overlap).
  - **Legal Glossary Card (`LegalGlossaryCard`):** Distinct amber container displaying term, definition, usage example, jurisdiction, source provenance (Black's Law Dictionary), and educational boundary notice. Kept strictly separate from WordNet.
  - **Candidate Senses Ranking (`CandidateSenseItem`):** Ranked WordNet synsets displaying synset ID, algorithmic score (not probabilities), definition, usage examples, and lexical relations.
  - **Evidence Panel (`EvidencePanel`):** Itemized token overlaps between sentence context and candidate gloss/examples/relations.
  - **3D Lexical Network Toggle:** Seamlessly displays the interactive Three.js 3D lexical network for the analyzed term.

### C. Distinctive 3D Lexical Network (`LexicalNetwork3D`)
- **3D Orbital Graph (Three.js):**
  - **Target Node (Center):** Prominent gold-brass sphere representing the target term.
  - **Candidate Synset Nodes (Orbit 1):** Color-coded spheres positioned in orbit around the target (selected sense highlighted in deep amber).
  - **Lexical Relation Nodes (Orbit 2):** Distinct emerald (hypernym), sky blue (hyponym), and purple (synonym) satellite nodes linked with transparent connecting edges.
- **Interactivity:**
  - Interactive raycasting: hovering/clicking nodes displays an informative inspection tooltip with definition and relations.
  - Camera reset and auto-rotation toggle controls.
- **Accessibility & Fallback:**
  - Accessible 2D table fallback available on demand via one-click toggle.
  - Automatic graceful fallback to the 2D table if WebGL is unavailable or fails to initialize.
  - Respects `prefers-reduced-motion` media queries.

### D. Document Analysis Workspace (`/document-analysis`)
- **Upload Zone (`DocumentUploadZone`):** Drag-and-drop zone supporting `.txt` and `.pdf` files.
- **Client-Side Validation:** Enforces 5 MB file size limit and accepted file extensions before uploading.
- **Document Metadata Card (`DocumentMetadataCard`):** Displays Document ID, filename, format, character count, page count, and passage count.
- **Scanned PDF Warning:** Clearly informs the user if a PDF contains zero extractable text (no scanned-PDF OCR claimed).
- **Passage Occurrence Viewer (`PassageOccurrenceViewer`):**
  - Search/filter input to quickly filter detected legal terms.
  - Master list of occurrences displaying term, passage ID, page number, and selected sense.
  - Detail view showing full sentence context, candidate ranking, and lexical relations.

### E. Corpus Search Workspace (`/search`)
- **Query Input & Samples:** Natural language query field with sample query pills ("contract consideration", "motion to dismiss", "confidentiality obligation").
- **Top-K Selector:** Slider for selecting 1 to 20 ranked passages.
- **Ranked Result Cards (`SearchResultCard`):**
  - Passage text with document title and page reference.
  - Matched term badges.
  - Retrieval score and method indicator (`tfidf_lexical_wsd`).
  - Score interpretation disclaimer clarifying that scores reflect retrieval ranking rather than legal correctness.

### F. Settings Workspace (`/settings`)
- **Base URL Configuration:** Allows configuring custom Flask backend base URLs (stored in browser `localStorage`).
- **Live Health Test:** Tests connectivity against `GET /health` with real-time latency reporting and diagnostic information.
- **Security Notice:** Reaffirms that API secrets and keys remain strictly on the Flask server and are never present in frontend bundles.

---

## 4. UI Component Library (Customized shadcn/ui)

Built using Tailwind CSS v4 and standard accessible primitives:
- `Button.jsx`: Primary, secondary, outline, ghost, and destructive variants with loading states.
- `Card.jsx`: Semantic card container with header, title, description, content, and footer sections.
- `Badge.jsx`: Compact metadata badges with color schemes for status, scores, and parts of speech.
- `Input.jsx` & `Textarea.jsx`: Accessible form controls with visible focus rings and error styling.
- `Alert.jsx`: Accessible status callouts for informational, warning, and error messages.
- `Tabs.jsx`: Accessible tab navigation for switching between views.
- `Skeleton.jsx`: Smooth placeholder loaders during in-flight network requests.

---

## 5. Motion Design (GSAP)

GSAP is used deliberately and selectively:
- Initial page entrance animations.
- Staggered entrance for candidate sense cards.
- Subtle emphasis transitions when selecting candidate senses or toggling the 3D network.
- All animations are cleaned up on component unmount and respect `prefers-reduced-motion`.

---

## 6. API Client & Networking Rules

- Built on standard browser `fetch` in `frontend/src/lib/api/client.js`.
- Uses `AbortController` for finite request timeouts (5s for health, 30s for analysis/search, 60s for document processing).
- Centralized `ApiException` parsing with structured error codes (`NETWORK_FAILURE`, `TIMEOUT`, `INVALID_REQUEST`, `FILE_TOO_LARGE`, `UNSUPPORTED_FORMAT`).
- TanStack Query v5 manages request lifecycles, background updates, and loading/error states without caching sensitive document uploads.
