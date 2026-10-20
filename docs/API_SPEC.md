# LegalSense — Flask API Specification

**Base URL (local example):** `http://127.0.0.1:5000`  
**Content type:** `application/json`, except multipart document upload  
**Status:** Verified implementation matching `src/legalsense/api.py`.

## 1. `GET /health`

Purpose: lightweight health check.

Example response (HTTP 200):
```json
{
  "status": "ok",
  "service": "legalsense-api",
  "wsd_ready": true,
  "llm_enabled": false
}
```

No credentials, filesystem secrets, or internal stack traces are returned.

## 2. `POST /api/v1/analyze`

Analyze text and optionally a target word.

Example request:
```json
{
  "text": "The parties provided consideration under the contract.",
  "target_word": "consideration",
  "use_llm": false
}
```

- `text` (string, required): Sentence or paragraph to analyze (up to 50,000 characters).
- `target_word` (string, optional): Specific word to disambiguate. If omitted, the engine automatically detects legal glossary terms and candidate ambiguous words in the text.
- `use_llm` (boolean, optional, default `false`): Request optional Groq contextual assistance if configured on the server.

Example response (HTTP 200):
```json
{
  "request_id": "9a0a1a06-b391-4560-bf8b-70f907e59b20",
  "results": [
    {
      "term": "consideration",
      "sentence": "The parties provided consideration under the contract.",
      "lemma": "consideration",
      "pos": "NOUN",
      "candidate_senses": [
        {
          "source": "wordnet",
          "synset_id": "circumstance.n.03",
          "definition": "information that should be kept in mind when making a decision",
          "pos": "NOUN",
          "score": 1.5,
          "rank": 1,
          "relations": {
            "synonyms": ["circumstance", "condition"],
            "hypernyms": ["information.n.02"],
            "hyponyms": ["mitigating_circumstance.n.01", "justification.n.01"]
          }
        }
      ],
      "selected_sense": {
        "source": "wordnet",
        "synset_id": "circumstance.n.03",
        "definition": "information that should be kept in mind when making a decision",
        "pos": "NOUN",
        "score": 1.5,
        "rank": 1,
        "relations": {
          "synonyms": ["circumstance", "condition"],
          "hypernyms": ["information.n.02"],
          "hyponyms": ["mitigating_circumstance.n.01", "justification.n.01"]
        }
      },
      "selection_method": "extended_lesk",
      "evidence": [
        {
          "candidate_synset_id": "circumstance.n.03",
          "overlap_tokens": ["the"],
          "overlap_source": "examples",
          "contribution": 1.0
        }
      ],
      "uncertain": true,
      "source_provenance": ["wordnet", "legal_glossary"],
      "legal_glossary_entry": {
        "term": "consideration",
        "definition": "Something of value exchanged between parties to a contract, such as money, services, or a promise, which is necessary to make the contract legally enforceable.",
        "jurisdiction": "Common law (general)",
        "source": "Black's Law Dictionary (general concept; simplified for educational use)",
        "usage_example": "The buyer provided adequate consideration by agreeing to pay $10,000 for the property.",
        "limitations": "This is an educational summary. Specific legal requirements for consideration vary by jurisdiction. Consult a qualified legal professional for authoritative guidance."
      },
      "llm_assistance_status": "disabled",
      "llm_suggested_sense": null,
      "llm_rationale": null
    }
  ],
  "warnings": []
}
```

## 3. `POST /api/v1/documents/analyze`

Multipart form fields:
- `file` (binary, required): TXT (`.txt`) or PDF (`.pdf`) document.
- `use_llm` (string boolean, optional, default `"false"`).

Example response (HTTP 200):
```json
{
  "request_id": "76ec2e5b-436f-4022-902e-c5db983577d6",
  "document_id": "doc_2331a4d20d4e",
  "filename": "lease_agreement.pdf",
  "file_type": "pdf",
  "character_count": 151,
  "page_count": 1,
  "passage_count": 1,
  "occurrences_analyzed": [
    {
      "term": "consideration",
      "page": 1,
      "passage_id": "doc_2331a4d20d4e_p001",
      "sentence": "The tenant provided adequate consideration for the execution of the lease.",
      "lemma": "consideration",
      "pos": "NOUN",
      "candidate_senses": [ ... ],
      "selected_sense": { ... },
      "selection_method": "extended_lesk",
      "evidence": [ ... ],
      "uncertain": true,
      "source_provenance": ["wordnet", "legal_glossary"],
      "legal_glossary_entry": { ... },
      "llm_assistance_status": "disabled",
      "llm_suggested_sense": null,
      "llm_rationale": null
    }
  ],
  "warnings": []
}
```

Requirements enforced:
- File size limit enforced via `LEGAL_SENSE_MAX_UPLOAD_MB` (HTTP 413 on excess).
- Unsupported extensions rejected (HTTP 415).
- Scanned / image-only PDFs flagged with informational warnings.
- Uploads are processed in-memory and not permanently saved to disk.

## 4. `POST /api/v1/search`

Search passages across indexed legal corpus using TF-IDF, lexical matching, and legal glossary signals.

Example request:
```json
{
  "query": "consideration exchanged under a contract",
  "top_k": 5,
  "use_llm": false
}
```

Example response (HTTP 200):
```json
{
  "query": "consideration exchanged under a contract",
  "results": [
    {
      "document_id": "doc_7343f7a0896c",
      "document_name": "sample_court_ruling.txt",
      "page": null,
      "passage": "IN THE APPELLATE COURT OF CIVIL APPEALS... The appellant contends that adequate consideration was present in the form of mutual promises exchanged upon execution of the underlying instrument...",
      "score": 0.3262,
      "score_method": "tfidf_lexical_wsd",
      "matched_terms": [
        "consideration",
        "exchanged"
      ]
    }
  ],
  "warnings": []
}
```

## 5. Error format

All errors return a consistent JSON payload:
```json
{
  "error": {
    "code": "INVALID_REQUEST",
    "message": "Field 'text' is required and must be a non-empty string."
  }
}
```

Status codes:
- `400` — Invalid or missing request input, missing parameters, empty files.
- `413` — File upload exceeds configured size limit (`FILE_TOO_LARGE`).
- `415` — Unsupported file format (`UNSUPPORTED_FORMAT`).
- `500` — Unexpected internal server error (sanitized message, no stack trace exposed).
- `503` — Service unavailable (e.g. search index uninitialized).

## 6. Implementation rules

- Secrets (`GROQ_API_KEY`) are kept server-side only.
- Groq request timeout is 6.0 seconds with safe fallback.
- No database or permanent user-upload storage.
