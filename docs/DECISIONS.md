# LegalSense — Architecture and Scope Decisions

Record all key architectural and implementation decisions, including rationale and consequences.

## D-001 — JavaFX frontend
**Decision:** Use Java + JavaFX.  
**Rationale:** User explicitly requires Java for the frontend and has rejected Streamlit.  
**Consequence:** Python remains the backend/NLP layer; frontend communicates over HTTP/JSON.

## D-002 — Python Flask backend
**Decision:** Use Flask for REST endpoints.  
**Rationale:** Lightweight, familiar and sufficient for the prototype.

## D-003 — WordNet and Extended Lesk remain core
**Decision:** WSD must be implemented and evaluated, not replaced by an LLM.  
**Rationale:** The assignment explicitly asks for WordNet, lexical relations and WSD.

## D-004 — Groq is optional
**Decision:** Groq API may assist with contextual analysis but must not be required.  
**Rationale:** Free-tier quotas and availability can change; core operation must remain reliable.

## D-005 — No local transformer on Render
**Decision:** Do not load or deploy transformer weights on Render's free web service.  
**Rationale:** Resource limits and cold starts make this unsuitable for the short project timeline.

## D-006 — Lightweight retrieval first
**Decision:** Begin with TF-IDF and lexical/WSD-aware ranking.  
**Rationale:** Avoids memory-heavy local embedding inference and reduces integration risk.

## D-007 — No database in first release
**Decision:** Use bundled sample corpus and request-scoped uploads.  
**Rationale:** A small prototype does not need persistence; Render free filesystem persistence must not be assumed.

## D-008 — Legal glossary is distinct from WordNet
**Decision:** Store curated legal definitions with source/provenance metadata.  
**Rationale:** WordNet covers general English and cannot be treated as an authoritative legal ontology.

## D-009 — Four phases
**Decision:** Implement WSD, API/document intelligence, JavaFX integration, then evaluation/deployment.  
**Rationale:** Enables early validation and limits integration risk within 3–4 days.

## D-010 — PyMuPDF 1.24.x pin for PDF extraction
**Decision:** Pin `PyMuPDF>=1.24.0,<1.25.0`.  
**Rationale:** PyMuPDF 2.0 introduced heavy neural dependencies (`onnxruntime`, `protobuf`, `networkx`, 63MB wheel), which violates our lightweight deployment constraint on Render. PyMuPDF 1.24.x provides fast, native C-based PDF text and page extraction with a 16MB footprint and zero heavy ML dependencies.  
**Consequence:** Clean, reproducible builds on Render and local machines.

## D-011 — In-memory stream ingestion without disk persistence
**Decision:** Ingest and segment uploaded files directly from memory streams (`io.BytesIO`).  
**Rationale:** Protects confidentiality of uploaded legal documents and eliminates dependence on Render's ephemeral filesystem.  
**Consequence:** Zero disk cleanup overhead and zero risk of file leakage across requests.

## D-012 — Compound TF-IDF, lexical, and legal glossary retrieval ranking
**Decision:** Combine TF-IDF cosine similarity with query lexical overlap and domain glossary boost.  
**Rationale:** Pure TF-IDF struggles on short legal clauses; adding exact lexical overlap and legal glossary boosting highlights passages that are both contextually relevant and legally significant.  
**Consequence:** Explainable, deterministic passage ranking without neural embeddings.

## D-013 — Strict candidate whitelist validation for Groq suggestions
**Decision:** Require Groq contextual suggestions to match an existing WordNet candidate synset ID or abstain.  
**Rationale:** LLMs are prone to hallucinating non-existent WordNet synsets or definitions. Validating against the candidate inventory guarantees that the response remains grounded in real WordNet data.  
**Consequence:** Hallucinated synsets are safely discarded, preserving local WSD predictions.

## D-014 — OpenJDK 21 LTS and Apache Maven 3.9.6 with Maven Wrapper
**Decision:** Standardize desktop client build on OpenJDK 21 LTS and Apache Maven 3.9.6, bundled with `mvnw.cmd` and `mvnw` wrappers.  
**Rationale:** Java 21 provides a stable modern LTS platform with built-in `HttpClient`, while the Maven wrapper guarantees reproducible builds across any environment without pre-installed Maven.  
**Consequence:** Clean, cross-platform builds with zero global tool installation hurdles.

## D-015 — Non-blocking asynchronous API client using java.net.http.HttpClient
**Decision:** Implement all REST endpoints (`checkHealth`, `analyzeText`, `analyzeDocument`, `searchCorpus`) asynchronously using Java's built-in `HttpClient` returning `CompletableFuture<T>`.  
**Rationale:** Network calls must never execute on the JavaFX Application Thread, which would freeze the GUI during PDF ingestion or network latency. All UI updates are marshaled back via `Platform.runLater()`.  
**Consequence:** Fluid, responsive user interface with visible progress indicators and disable guards against duplicate submissions.

## D-016 — Jackson 2.17.0 with resilient schema tolerance
**Decision:** Use Jackson Databind configured with `DeserializationFeature.FAIL_ON_UNKNOWN_PROPERTIES = false`.  
**Rationale:** Legal NLP response envelopes contain multiple optional and experimental fields (e.g. LLM suggestions, passage offsets, evidence overlaps). Tolerating unknown properties ensures client forward-compatibility and prevents crashes when API schemas evolve.  
**Consequence:** Robust deserialization and structured error mapping.

## D-017 — Non-modular classpath launcher for JavaFX 21
**Decision:** Provide a secondary `com.legalsense.Launcher` main class that calls `LegalSenseApp.main(args)`.  
**Rationale:** Under Java 11+, launching a JavaFX `Application` subclass directly from the classpath without `--module-path` flags can throw a runtime exception. A non-inheriting launcher class bypasses this check cleanly.  
**Consequence:** Enables standard execution via `.\mvnw.cmd javafx:run` and `.\mvnw.cmd exec:java`.

## D-018 — Stopword filtering in Extended Lesk WSD
**Decision:** Filter high-frequency English stopwords (`nltk.corpus.stopwords.words('english')`) from context sentences and relation gloss/example strings during Lesk overlap scoring.  
**Rationale:** Unfiltered token matching permitted non-content words (e.g., `the`, `by`, `from`, `of`) to score spurious points against lengthy WordNet definitions, artificially favoring verbose non-legal senses over concise legal senses.  
**Consequence:** Accuracy on legal-domain contexts surged from 50.0% to 80.0%, and overall benchmark accuracy rose from 44.83% to 55.17%.

## D-019 — Manually annotated legal WSD evaluation benchmark and MFS baseline
**Decision:** Construct a 30-instance manually annotated benchmark across 10 polysemous legal terms with exact Princeton WordNet 3.0 gold synset IDs and rationales, comparing against a Most Frequent Sense (MFS) baseline.  
**Rationale:** Transparent academic evaluation requires reproducible gold annotations and a standard baseline rather than arbitrary assertions.  
**Consequence:** Proven superiority of domain-aware Extended Lesk (80.0% legal accuracy) over general corpus frequency baseline (10.0% legal accuracy).

## D-020 — Explicit abstention and out-of-WordNet handling for domain polysemy
**Decision:** If all candidate WordNet synsets score 0.0 or if a legal concept (e.g. contractual consideration as bargained-for exchange) is absent from WordNet, the engine abstains (`selected_sense = None`, `uncertain = True`) and returns the curated legal glossary entry instead.  
**Rationale:** Princeton WordNet was designed as a general-English lexical database and lacks specialized legal senses. Forcing an arbitrary WordNet mapping would produce dangerously misleading legal conclusions.  
**Consequence:** Preserves legal fidelity and transparency, achieving 92.31% selective accuracy when the engine is confident.

