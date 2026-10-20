# Antigravity Workflow — LegalSense

## Mandatory instructions for every phase

You are implementing LegalSense in the current repository. Before coding:
1. Inspect the repository tree, existing code, dependency files and README.
2. Read `README.md`, `docs/PRD.md`, `docs/ARCHITECTURE.md`, `docs/DECISIONS.md`, `docs/PHASE_PLAN.md`, and the documents relevant to the requested phase.
3. Identify existing functionality and avoid duplicate implementations.
4. State a short execution plan, then implement the requested phase rather than stopping at recommendations.
5. Preserve working code and existing user changes.

## Phase boundaries

- Phase 1: WSD engine only.
- Phase 2: document processing, retrieval and Flask API.
- Phase 3: JavaFX frontend and API integration.
- Phase 4: evaluation, hardening, deployment and final report.

Do not implement future phases prematurely unless a minimal interface contract is required.

## Coding standards

- Keep modules small and responsibilities separate.
- Use type hints where practical.
- Add meaningful error handling.
- Avoid unnecessary dependencies.
- Do not fabricate WordNet senses, legal definitions, citations, metrics or deployment results.
- Keep Groq optional.
- Do not add a local transformer model requirement.
- Do not add Streamlit.
- Never expose API keys.
- Update documentation when API contracts or setup steps change.

## Verification requirements

After implementation:
1. Run the relevant tests.
2. Run the application or endpoint where possible.
3. Report exact commands and actual outcomes.
4. List created/modified files.
5. List failures, skipped tests and unresolved issues.
6. Do not say a feature works unless it has been tested.

## Scope discipline

The target is a working prototype in 3–4 days. Avoid authentication, database persistence, OCR, large crawlers, cloud model hosting and unrelated features unless the user explicitly approves a scope change.
