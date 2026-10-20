"""Flask REST API implementation for LegalSense.

Implements all endpoints defined in docs/API_SPEC.md:
- GET /health
- POST /api/v1/analyze
- POST /api/v1/documents/analyze
- POST /api/v1/search

Includes strict request validation, consistent error responses,
safe resource limits, and optional Groq contextual assistance with
local fallback.
"""

from __future__ import annotations

import logging
import os
import uuid
from pathlib import Path
from typing import Any, Optional

from flask import Blueprint, Flask, jsonify, request
from werkzeug.exceptions import HTTPException, RequestEntityTooLarge

from legalsense.document_ingestion import (
    DocumentValidationError,
    get_max_upload_bytes,
    ingest_document,
)
from legalsense.groq_adapter import is_llm_enabled, query_groq_wsd_assistance
from legalsense.legal_glossary import load_glossary, lookup_term
from legalsense.lesk_wsd import disambiguate, disambiguate_all_targets
from legalsense.preprocessing import preprocess, tokenize_gloss
from legalsense.retrieval import PassageRetriever
from legalsense.schemas import CandidateSense, WSDResult
from legalsense.segmentation import segment_document, segment_text
from legalsense.wordnet_service import ensure_wordnet

logger = logging.getLogger(__name__)

bp = Blueprint("api", __name__)

# Maximum text length for single-request text analysis (50,000 characters)
MAX_TEXT_LENGTH = 50_000


def error_response(message: str, code: str = "INVALID_REQUEST", status_code: int = 400):
    """Generate a consistent JSON error response matching API_SPEC.md § 5."""
    return jsonify({
        "error": {
            "code": code,
            "message": message,
        }
    }), status_code


def serialize_candidate_sense(candidate: CandidateSense) -> dict[str, Any]:
    """Serialize CandidateSense according to API_SPEC.md § 2."""
    return {
        "source": candidate.source,
        "synset_id": candidate.synset_id,
        "definition": candidate.definition,
        "pos": candidate.pos,
        "score": round(candidate.score, 4),
        "rank": candidate.rank,
        "relations": {
            "synonyms": candidate.lemma_names,
            "hypernyms": candidate.hypernyms,
            "hyponyms": candidate.hyponyms,
        },
    }


def serialize_wsd_result(
    result: WSDResult,
    llm_status: str = "disabled",
    llm_suggested_id: Optional[str] = None,
    llm_rationale: Optional[str] = None,
) -> dict[str, Any]:
    """Serialize WSDResult according to API_SPEC.md § 2."""
    selected_dict = (
        serialize_candidate_sense(result.selected_sense)
        if result.selected_sense
        else None
    )

    glossary_dict = None
    if result.legal_glossary_entry:
        glossary_dict = {
            "term": result.legal_glossary_entry.term,
            "definition": result.legal_glossary_entry.definition,
            "source": result.legal_glossary_entry.source,
            "jurisdiction": result.legal_glossary_entry.jurisdiction,
            "usage_example": result.legal_glossary_entry.usage_example,
            "limitations": result.legal_glossary_entry.limitations,
        }

    evidence_list = [
        {
            "candidate_synset_id": ev.candidate_synset_id,
            "overlap_tokens": ev.overlap_tokens,
            "overlap_source": ev.overlap_source,
            "contribution": round(ev.contribution, 4),
        }
        for ev in result.evidence
    ]

    return {
        "term": result.term,
        "sentence": result.sentence,
        "pos": result.pos,
        "lemma": result.lemma,
        "candidate_senses": [serialize_candidate_sense(c) for c in result.candidate_senses],
        "selected_sense": selected_dict,
        "selection_method": result.selection_method,
        "evidence": evidence_list,
        "uncertain": result.uncertain,
        "source_provenance": result.source_provenance,
        "legal_glossary_entry": glossary_dict,
        "llm_assistance_status": llm_status,
        "llm_suggested_sense": llm_suggested_id,
        "llm_rationale": llm_rationale,
    }


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@bp.route("/health", methods=["GET"])
def health():
    """Health check endpoint per docs/API_SPEC.md § 1."""
    return jsonify({
        "status": "ok",
        "service": "legalsense-api",
        "wsd_ready": ensure_wordnet(),
        "llm_enabled": is_llm_enabled(),
    }), 200


@bp.route("/api/v1/analyze", methods=["POST"])
def analyze():
    """Text analysis endpoint per docs/API_SPEC.md § 2."""
    if not request.is_json:
        return error_response(
            "Request must be JSON with Content-Type: application/json.",
            code="INVALID_CONTENT_TYPE",
            status_code=400,
        )

    try:
        body = request.get_json(silent=False)
    except Exception as exc:
        return error_response(f"Malformed JSON body: {exc}", code="MALFORMED_JSON", status_code=400)

    if not isinstance(body, dict):
        return error_response("Request body must be a JSON object.", code="INVALID_BODY", status_code=400)

    text = body.get("text")
    if not text or not isinstance(text, str) or not text.strip():
        return error_response("Field 'text' is required and must be a non-empty string.", code="MISSING_TEXT", status_code=400)

    if len(text) > MAX_TEXT_LENGTH:
        return error_response(
            f"Field 'text' exceeds maximum length of {MAX_TEXT_LENGTH} characters.",
            code="TEXT_TOO_LONG",
            status_code=400,
        )

    target_word = body.get("target_word")
    if target_word is not None and (not isinstance(target_word, str) or not target_word.strip()):
        return error_response("Field 'target_word' when provided must be a non-empty string.", code="INVALID_TARGET_WORD", status_code=400)

    use_llm = bool(body.get("use_llm", False))
    request_id = str(uuid.uuid4())
    warnings: list[str] = []

    # Determine terms to disambiguate
    target_terms: list[str] = []
    if target_word:
        target_terms = [target_word.strip()]
    else:
        # Automatically detect target words present in legal glossary
        glossary = load_glossary()
        tokens = set(tokenize_gloss(text))
        matched_glossary_terms = [term for term in glossary.keys() if term in tokens]
        if matched_glossary_terms:
            target_terms = sorted(matched_glossary_terms)
        else:
            # Fallback to key content words with WordNet senses
            pre = preprocess(text)
            candidates = [t.lemma for t in pre.content_tokens() if t.pos in ["NOUN", "VERB"] and len(t.lemma) > 2]
            target_terms = sorted(set(candidates))[:5]  # limit to top 5 detected words

    if not target_terms:
        warnings.append("No specific target words could be identified in the input text for disambiguation.")

    results: list[dict[str, Any]] = []

    for term in target_terms:
        legal_entry = lookup_term(term)
        wsd_res = disambiguate(text, term, legal_entry=legal_entry)

        llm_status = "disabled"
        llm_suggested_id = None
        llm_rationale = None

        if use_llm:
            if is_llm_enabled():
                llm_res = query_groq_wsd_assistance(
                    sentence=text,
                    target_word=term,
                    candidates=wsd_res.candidate_senses,
                    legal_entry=legal_entry,
                )
                llm_status = llm_res.status
                llm_suggested_id = llm_res.suggested_synset_id
                llm_rationale = llm_res.rationale
                if llm_res.warning:
                    warnings.append(f"[{term}] LLM note: {llm_res.warning}")
            else:
                llm_status = "disabled"
                warnings.append("LLM assistance requested but GROQ_API_KEY is not configured or enabled.")

        serialized = serialize_wsd_result(
            wsd_res,
            llm_status=llm_status,
            llm_suggested_id=llm_suggested_id,
            llm_rationale=llm_rationale,
        )
        results.append(serialized)

    return jsonify({
        "request_id": request_id,
        "results": results,
        "warnings": warnings,
    }), 200


@bp.route("/api/v1/documents/analyze", methods=["POST"])
def analyze_document():
    """Document upload and analysis endpoint per docs/API_SPEC.md § 3."""
    if "file" not in request.files:
        return error_response(
            "Multipart form must include a 'file' field.",
            code="MISSING_FILE",
            status_code=400,
        )

    file_item = request.files["file"]
    if not file_item or not file_item.filename or not file_item.filename.strip():
        return error_response(
            "No file was selected or uploaded.",
            code="EMPTY_FILENAME",
            status_code=400,
        )

    use_llm_raw = request.form.get("use_llm", "false")
    use_llm = use_llm_raw.lower() in ["true", "1", "yes"]

    # Ingest document
    try:
        doc = ingest_document(file_item.stream, filename=file_item.filename)
    except DocumentValidationError as exc:
        status_code = 400
        if exc.code == "FILE_TOO_LARGE":
            status_code = 413
        elif exc.code == "UNSUPPORTED_FORMAT":
            status_code = 415
        return error_response(exc.message, code=exc.code, status_code=status_code)
    except Exception as exc:
        logger.exception("Unexpected error during document ingestion: %s", exc)
        return error_response("An unexpected error occurred during document extraction.", code="INGESTION_ERROR", status_code=500)

    # Segment document into passages
    passages = segment_document(doc)

    # Find legal glossary terms across passages
    glossary = load_glossary()
    occurrences_analyzed: list[dict[str, Any]] = []
    warnings = list(doc.warnings)

    if doc.is_scanned_or_empty:
        warnings.append("No text could be extracted from the document to analyze.")
    else:
        # Scan passages for glossary terms
        for passage in passages:
            passage_tokens = set(tokenize_gloss(passage.text))
            matched_terms = [t for t in glossary.keys() if t in passage_tokens]

            for term in matched_terms:
                legal_entry = glossary[term]
                wsd_res = disambiguate(passage.text, term, legal_entry=legal_entry)

                llm_status = "disabled"
                llm_suggested_id = None
                llm_rationale = None

                if use_llm and is_llm_enabled():
                    llm_res = query_groq_wsd_assistance(
                        sentence=passage.text,
                        target_word=term,
                        candidates=wsd_res.candidate_senses,
                        legal_entry=legal_entry,
                    )
                    llm_status = llm_res.status
                    llm_suggested_id = llm_res.suggested_synset_id
                    llm_rationale = llm_res.rationale

                ser = serialize_wsd_result(
                    wsd_res,
                    llm_status=llm_status,
                    llm_suggested_id=llm_suggested_id,
                    llm_rationale=llm_rationale,
                )
                ser["page"] = passage.page
                ser["passage_id"] = passage.passage_id
                occurrences_analyzed.append(ser)

    request_id = str(uuid.uuid4())
    return jsonify({
        "request_id": request_id,
        "document_id": doc.document_id,
        "filename": doc.filename,
        "file_type": doc.file_type,
        "character_count": doc.total_characters,
        "page_count": len(doc.pages),
        "passage_count": len(passages),
        "occurrences_analyzed": occurrences_analyzed,
        "warnings": warnings,
    }), 200


@bp.route("/api/v1/search", methods=["POST"])
def search():
    """Corpus search endpoint per docs/API_SPEC.md § 4."""
    if not request.is_json:
        return error_response(
            "Request must be JSON with Content-Type: application/json.",
            code="INVALID_CONTENT_TYPE",
            status_code=400,
        )

    try:
        body = request.get_json(silent=False)
    except Exception as exc:
        return error_response(f"Malformed JSON body: {exc}", code="MALFORMED_JSON", status_code=400)

    if not isinstance(body, dict):
        return error_response("Request body must be a JSON object.", code="INVALID_BODY", status_code=400)

    query = body.get("query")
    if not query or not isinstance(query, str) or not query.strip():
        return error_response("Field 'query' is required and must be a non-empty string.", code="MISSING_QUERY", status_code=400)

    top_k_raw = body.get("top_k", 5)
    try:
        top_k = int(top_k_raw)
        if top_k < 1 or top_k > 100:
            raise ValueError
    except (TypeError, ValueError):
        return error_response("Field 'top_k' must be an integer between 1 and 100.", code="INVALID_TOP_K", status_code=400)

    from flask import current_app
    retriever: PassageRetriever = current_app.config.get("RETRIEVER")
    if retriever is None:
        return error_response("Search index is not initialized.", code="SEARCH_UNAVAILABLE", status_code=503)

    search_results = retriever.search(query, top_k=top_k)
    serialized_results = [r.to_dict() for r in search_results]

    warnings: list[str] = []
    if not serialized_results:
        warnings.append("No matching passages found for query.")

    return jsonify({
        "query": query,
        "results": serialized_results,
        "warnings": warnings,
    }), 200


# ---------------------------------------------------------------------------
# Application Factory
# ---------------------------------------------------------------------------

def load_default_corpus() -> PassageRetriever:
    """Load and index bundled sample legal documents for search."""
    project_root = Path(__file__).resolve().parent.parent.parent
    sample_dir = project_root / "data" / "sample_documents"

    all_passages = []
    if sample_dir.is_dir():
        for file_path in sorted(sample_dir.glob("*.txt")):
            try:
                doc = ingest_document(file_path)
                passages = segment_document(doc)
                all_passages.extend(passages)
            except Exception as exc:
                logger.warning("Could not index sample document %s: %s", file_path, exc)

    logger.info("Loaded default corpus with %d passages.", len(all_passages))
    return PassageRetriever(all_passages)


def create_app(test_config: Optional[dict[str, Any]] = None) -> Flask:
    """Create and configure the LegalSense Flask application."""
    app = Flask(__name__)

    # Configure maximum content length
    app.config["MAX_CONTENT_LENGTH"] = get_max_upload_bytes()

    # Apply test config if provided
    if test_config:
        app.config.update(test_config)

    # Initialize retriever if not already in config
    if "RETRIEVER" not in app.config:
        app.config["RETRIEVER"] = load_default_corpus()

    # Register blueprints
    app.register_blueprint(bp)

    # Error handlers
    @app.errorhandler(RequestEntityTooLarge)
    def handle_file_too_large(error):
        max_mb = get_max_upload_bytes() // (1024 * 1024)
        return error_response(
            f"File exceeds maximum upload size of {max_mb} MB.",
            code="FILE_TOO_LARGE",
            status_code=413,
        )

    @app.errorhandler(HTTPException)
    def handle_http_exception(error):
        return error_response(
            error.description or "HTTP error occurred.",
            code="HTTP_ERROR",
            status_code=error.code or 500,
        )

    @app.errorhandler(Exception)
    def handle_generic_exception(error):
        logger.exception("Unhandled server exception: %s", error)
        return error_response(
            "An unexpected internal server error occurred.",
            code="INTERNAL_SERVER_ERROR",
            status_code=500,
        )

    return app
