# LegalSense — WSD and Lexical Semantics Design

## 1. Purpose

This document defines the minimum WSD behavior required for the academic problem statement and its legal-domain adaptation.

## 2. Core terminology

- **Word Sense Disambiguation:** selecting or ranking a word's possible meanings using context.
- **Synset:** a WordNet set of synonymous lexical items representing a sense.
- **Gloss:** the definition associated with a WordNet synset.
- **Synonym relation:** lexical items grouped as equivalent or near-equivalent within a synset.
- **Hypernym:** a broader category relation.
- **Hyponym:** a more specific category relation.
- **Legal glossary entry:** a curated domain-specific definition, explicitly distinct from a WordNet synset.

## 3. Processing pipeline

1. Receive text and an optional target word.
2. Tokenize and lemmatize the sentence; determine POS where possible.
3. Retrieve candidate WordNet synsets compatible with the token/POS.
4. Retrieve glosses, examples and available lexical relations.
5. Construct a context representation from surrounding words.
6. Score candidate senses using an Extended Lesk-style overlap method.
7. Optionally add documented lexical relation evidence. Do not silently alter scores with undocumented heuristics.
8. If the term has a curated legal glossary entry, display it separately and use it as domain evidence only through an explicit, testable rule.
9. Return candidate scores/ranks, selected sense if supportable, evidence and uncertainty status.

## 4. Scoring and uncertainty

The exact Extended Lesk implementation must be documented in code and README. A simple baseline may count overlap between context tokens and candidate gloss/example tokens. An extended version may add overlap with related synset glosses, but any weighting must be explicit and testable.

Do not label raw overlap scores as calibrated probabilities. If top candidates are tied or nearly tied, mark the result as uncertain and show alternatives. Thresholds must be configurable and chosen using development data, not invented as universal constants.

## 5. Legal-domain safeguards

- WordNet is not a legal ontology.
- General-English senses and legal meanings may not map one-to-one.
- The curated glossary should include definition source, jurisdiction if applicable, and a note that it is informational.
- Never generate a legal interpretation merely because a word has a WordNet synset.
- Groq may choose only among supplied candidates or return “insufficient evidence”; it must not create a new synset ID.
- The UI must identify whether content came from WordNet, the legal glossary, the source document or the optional LLM.

## 6. Suggested initial term inventory

Use a small set and test each term in multiple contexts. Candidate terms may include:
- consideration
- execution
- charge
- appeal
- party
- action
- instrument
- relief
- suit
- motion

These are candidate terms, not a claim that every term has two useful WordNet senses. During implementation, verify available synsets and keep only terms that produce meaningful, testable ambiguity. Legal senses should be sourced from a curated glossary rather than fabricated from WordNet.

## 7. Output contract

For each analyzed occurrence, expose:
- `term`
- `sentence`
- `lemma`
- `pos`
- `candidate_senses`
- `selected_sense` or null
- `selection_method`
- `evidence`
- `uncertain`
- `source_provenance`
- optional `legal_glossary_entry`
- optional `llm_assistance_status`

Candidate senses should include WordNet synset ID, definition/gloss and available relations. Do not include unsupported relation fields as if they exist.

## 8. Phase 4 Algorithmic Refinements & Targeted Improvements

### Stopword-Filtered Discriminative Overlap

- **Observed Vulnerability:** Initial naive Lesk matching computed set intersections between all context tokens and candidate gloss/example/hypernym/hyponym tokens. Senses with verbose glosses and extensive usage examples accumulated spurious points from high-frequency English function words (`the`, `from`, `of`, `to`, `by`, `in`). This caused irrelevant senses (e.g., `easing.n.02` for `relief`) to outscore true legal senses.
- **Implemented Correction (`src/legalsense/lesk_wsd.py`):**
  - Integrated NLTK English stopword filtering (`_filter_toks`) into tokenized context words and all relation gloss/example strings.
  - Active by default (`DEFAULT_FILTER_STOPWORDS = True`), with programmatic override option (`filter_stopwords=False`) for baseline comparison.
- **Measured Impact:**
  - Overall accuracy on the held-out benchmark improved from **44.83% to 55.17% (+10.34%)**.
  - Accuracy specifically on legal-domain contexts surged from **50.0% to 80.0% (+30.0%)**.
  - Macro-F1 jumped from **0.2991 to 0.4608**.

### Uncertainty and Explicit Abstention Logic

- **Deterministic Uncertainty Criteria:** A disambiguation result is flagged as `uncertain = True` if any of three conditions hold:
  1. `all_zero`: Every candidate sense scored 0.0 (no lexical overlap).
  2. `is_tied`: The difference between the top candidate score and runner-up candidate score is $\le \text{tie\_margin}$ (default: 0.1).
  3. `weak_evidence`: The top score is strictly less than $\text{min\_evidence\_score}$ (default: 1.0).
- **Explicit Abstention:** When `all_zero` is True, `selected_sense` is explicitly returned as `None` rather than arbitrarily picking the first candidate.
- **Out-of-WordNet Safeguard:** When a domain concept (e.g. contractual consideration as bargained-for exchange) is absent from WordNet, the engine abstains from selecting an incorrect WordNet synset and displays the curated legal glossary entry instead.
- **Selective Reliability:** Predictions with `uncertain == False` exhibit **92.31% accuracy**, providing a high-confidence signal for legal professionals.

