# LegalSense — Product Requirements Document (PRD)

**Version:** 1.0  
**Status:** Implementation baseline  
**Project type:** Academic AIML/NLP project and working prototype

## 1. Product summary

LegalSense is a context-aware legal document analyzer that demonstrates Word Sense Disambiguation (WSD) using WordNet and lexical relations. It identifies selected ambiguous terms in legal text, presents candidate senses, estimates the contextually appropriate sense, exposes supporting lexical evidence, and retrieves relevant passages from a small document collection.

The project combines an explainable knowledge-based WSD baseline with lightweight semantic/lexical retrieval. A Groq-hosted LLM may optionally assist with difficult contextual interpretation, but the core system must not depend on the API.

## 2. Problem statement

Keyword search treats matching words as equivalent even when a word has different meanings in different contexts. In legal text, this can create irrelevant retrieval results and obscure distinctions between ordinary English and legal terminology.

LegalSense aims to improve document exploration by:
- detecting selected ambiguous words;
- generating candidate WordNet senses and lexical relations;
- scoring candidate senses against sentence context;
- incorporating a clearly identified, curated legal glossary;
- retrieving and ranking relevant passages;
- showing evidence and uncertainty instead of presenting unsupported certainty.

## 3. Goals

### Primary goals
1. Implement a working WSD algorithm based on WordNet and lexical relations.
2. Display candidate senses, definitions, examples, synonyms, hypernyms and hyponyms where available.
3. Analyze user-provided text and TXT/PDF legal documents.
4. Provide context-aware passage search over a small corpus.
5. Expose the backend through a documented Flask REST API.
6. Provide a JavaFX desktop frontend.
7. Evaluate WSD predictions on a manually annotated test set and document limitations.
8. Support deployment of the lightweight backend to Render without requiring a locally hosted transformer model.

### Non-goals
- Providing legal advice or definitive legal interpretations.
- Replacing a lawyer, legal researcher or authoritative legal database.
- Crawling large legal websites or building a comprehensive legal corpus.
- Supporting every legal jurisdiction, language or legal term.
- Training a large model from scratch.
- Requiring a paid API or hosted LLM for core operation.
- Implementing accounts, billing, collaboration or enterprise document management in the first version.

## 4. Target users

- Students learning NLP, lexical semantics and WSD.
- Legal studies students and researchers exploring public legal texts.
- Users who need a demonstrable prototype for context-sensitive document retrieval.

## 5. Primary user journeys

### Journey A — Analyze a sentence
1. User enters a sentence containing an ambiguous word.
2. System tokenizes and preprocesses the text.
3. System retrieves candidate senses from WordNet and the legal glossary where relevant.
4. WSD engine ranks candidates using contextual evidence.
5. UI displays the predicted sense, alternatives, lexical relations and uncertainty.

### Journey B — Analyze a document
1. User selects a TXT or PDF document.
2. Backend extracts text and divides it into passages.
3. The system identifies configured target terms and runs WSD on their occurrences.
4. UI displays analyzed terms and source-grounded passages.

### Journey C — Search legal passages
1. User enters a concept or phrase.
2. Backend ranks corpus passages using TF-IDF/lexical scoring and available WSD signals.
3. UI shows ranked passages with document/page references when available.
4. User can inspect the evidence for each result.

## 6. Functional requirements

| ID | Requirement | Priority |
|---|---|---|
| FR-01 | Retrieve WordNet synsets, glosses, examples and lexical relations | Must |
| FR-02 | Implement Lesk or Extended Lesk as an explainable WSD baseline | Must |
| FR-03 | Apply tokenization, lemmatization and POS-aware candidate filtering | Must |
| FR-04 | Provide a curated legal glossary clearly separated from WordNet data | Must |
| FR-05 | Return candidate senses, ranking evidence and uncertainty state | Must |
| FR-06 | Analyze user-provided plain text | Must |
| FR-07 | Extract text from TXT and PDF files | Must |
| FR-08 | Retrieve and rank relevant passages from a small corpus | Must |
| FR-09 | Provide Flask endpoints with validation and documented JSON schemas | Must |
| FR-10 | Build a JavaFX desktop frontend using Java HttpClient | Must |
| FR-11 | Continue core operation when Groq is unavailable or unconfigured | Must |
| FR-12 | Support Render deployment without loading a transformer model | Must |
| FR-13 | Evaluate WSD against manually annotated examples | Must |
| FR-14 | Produce report, setup instructions and test results | Must |
| FR-15 | Optionally call Groq for contextual assistance | Should |
| FR-16 | Show a clear explanation of source type and limitations | Must |

## 7. Non-functional requirements

- **Reliability:** API and UI failures should be handled without crashing the application.
- **Explainability:** Each WSD result should expose candidate definitions and available evidence.
- **Portability:** Local development should be possible using documented commands.
- **Resource awareness:** The Render service must not load large transformer models.
- **Privacy:** API keys remain server-side; do not send confidential documents to external APIs.
- **Maintainability:** Separate WSD, document extraction, retrieval, API and UI responsibilities.
- **Honest reporting:** Never fabricate accuracy, F1, deployment success or model capabilities.

## 8. Constraints

- Frontend: Java + JavaFX.
- Backend: Python + Flask.
- WSD resource: NLTK WordNet.
- WSD baseline: Lesk/Extended Lesk.
- Optional hosted LLM: Groq API.
- Deployment target: Render free web service, subject to current platform limits.
- Initial storage: bundled sample files and lightweight in-memory/indexed data; no database required.
- No Streamlit, no mandatory local transformer, and no mandatory API key.

## 9. Success criteria

The project is successful when:
1. A user can analyze text through JavaFX.
2. The backend returns candidate senses and lexical relations from WordNet.
3. WSD predictions are produced by a documented algorithm.
4. TXT/PDF input and passage search work end to end.
5. The system operates without a Groq key.
6. Tests and evaluation metrics are reproducible.
7. Render deployment is either verified with evidence or clearly marked as not yet verified.
8. The final report states limitations and does not claim legal authority.

## 10. Risk register

| Risk | Mitigation |
|---|---|
| WordNet lacks a useful legal sense | Add a curated legal glossary and label its source |
| Lesk has weak accuracy on some terms | Keep candidate rankings and uncertainty; evaluate errors |
| Groq quota or outage | Core local fallback; make LLM optional |
| Render cold starts/resource limits | Keep dependencies lightweight and avoid model loading |
| PDF extraction returns poor text | Validate extracted text and report scanned PDFs as unsupported unless OCR is added |
| Search results appear legally authoritative | Label them as informational retrieval, not legal advice |
| Evaluation set is too small | Disclose sample size and treat metrics as preliminary |

## 11. Definition of done

The application builds, runs, passes its documented tests, exposes the required WSD outputs, includes a JavaFX interface, and has a report with actual measured results and explicit limitations.
