"""Tests for the LegalSense Flask REST API."""

import io
import json
import pytest

from legalsense.api import create_app
from legalsense.retrieval import PassageRetriever
from legalsense.segmentation import Passage


@pytest.fixture
def app():
    """Create test application with in-memory test corpus."""
    test_passages = [
        Passage(
            passage_id="doc_test_p001",
            document_id="doc_test",
            document_name="test_contract.txt",
            text="The parties exchanged good and valuable consideration under the agreement upon execution.",
            page=1,
        ),
        Passage(
            passage_id="doc_test_p002",
            document_id="doc_test",
            document_name="test_contract.txt",
            text="In the event of a dispute, either party may file a formal action or suit in court.",
            page=2,
        ),
    ]
    test_retriever = PassageRetriever(test_passages)
    app = create_app({"TESTING": True, "RETRIEVER": test_retriever})
    return app


@pytest.fixture
def client(app):
    return app.test_client()


class TestHealthEndpoint:
    """Tests for GET /health."""

    def test_health_ok(self, client):
        res = client.get("/health")
        assert res.status_code == 200
        data = res.get_json()
        assert data["status"] == "ok"
        assert data["service"] == "legalsense-api"
        assert "wsd_ready" in data
        assert "llm_enabled" in data
        assert isinstance(data["wsd_ready"], bool)
        assert isinstance(data["llm_enabled"], bool)


class TestAnalyzeEndpoint:
    """Tests for POST /api/v1/analyze."""

    def test_valid_with_target_word(self, client):
        payload = {
            "text": "The parties provided consideration under the contract.",
            "target_word": "consideration",
            "use_llm": False,
        }
        res = client.post("/api/v1/analyze", json=payload)
        assert res.status_code == 200
        data = res.get_json()
        assert "request_id" in data
        assert "results" in data
        assert len(data["results"]) == 1

        r = data["results"][0]
        assert r["term"] == "consideration"
        assert r["pos"] == "NOUN"
        assert len(r["candidate_senses"]) > 0
        assert "relations" in r["candidate_senses"][0]
        assert "synonyms" in r["candidate_senses"][0]["relations"]
        assert "evidence" in r
        assert "selection_method" in r
        assert r["selection_method"] == "extended_lesk"
        assert r["legal_glossary_entry"] is not None
        assert r["legal_glossary_entry"]["term"] == "consideration"
        assert r["llm_assistance_status"] == "disabled"

    def test_valid_without_target_word_detects_terms(self, client):
        payload = {
            "text": "The party filed an action in the court seeking equitable relief.",
            "use_llm": False,
        }
        res = client.post("/api/v1/analyze", json=payload)
        assert res.status_code == 200
        data = res.get_json()
        assert len(data["results"]) >= 1
        terms = [r["term"] for r in data["results"]]
        # Should detect glossary terms like 'party', 'action', or 'relief'
        assert any(t in terms for t in ["party", "action", "relief"])

    def test_non_json_content_type(self, client):
        res = client.post("/api/v1/analyze", data="plain text not json")
        assert res.status_code == 400
        data = res.get_json()
        assert "error" in data
        assert data["error"]["code"] == "INVALID_CONTENT_TYPE"

    def test_missing_text(self, client):
        res = client.post("/api/v1/analyze", json={"target_word": "bank"})
        assert res.status_code == 400
        data = res.get_json()
        assert data["error"]["code"] == "MISSING_TEXT"

    def test_empty_text(self, client):
        res = client.post("/api/v1/analyze", json={"text": "   "})
        assert res.status_code == 400
        data = res.get_json()
        assert data["error"]["code"] == "MISSING_TEXT"

    def test_oversized_text(self, client):
        res = client.post("/api/v1/analyze", json={"text": "A" * 50_001})
        assert res.status_code == 400
        data = res.get_json()
        assert data["error"]["code"] == "TEXT_TOO_LONG"

    def test_invalid_target_word(self, client):
        res = client.post("/api/v1/analyze", json={"text": "Valid text.", "target_word": ""})
        assert res.status_code == 400
        data = res.get_json()
        assert data["error"]["code"] == "INVALID_TARGET_WORD"


class TestDocumentAnalyzeEndpoint:
    """Tests for POST /api/v1/documents/analyze."""

    def test_valid_txt_upload(self, client):
        content = (
            b"STANDARD AGREEMENT\n\n"
            b"The buyer provided adequate consideration for the execution of the commercial deed.\n\n"
            b"Both parties signed the instrument in good faith."
        )
        data = {
            "file": (io.BytesIO(content), "agreement.txt"),
            "use_llm": "false",
        }
        res = client.post(
            "/api/v1/documents/analyze",
            data=data,
            content_type="multipart/form-data",
        )
        assert res.status_code == 200
        resp_data = res.get_json()
        assert "request_id" in resp_data
        assert "document_id" in resp_data
        assert resp_data["filename"] == "agreement.txt"
        assert resp_data["file_type"] == "txt"
        assert resp_data["character_count"] > 0
        assert resp_data["passage_count"] >= 1
        assert "occurrences_analyzed" in resp_data
        # Terms like 'consideration', 'execution', 'party', 'instrument' should be analyzed
        analyzed_terms = [o["term"] for o in resp_data["occurrences_analyzed"]]
        assert any(t in analyzed_terms for t in ["consideration", "execution", "instrument", "party"])

    def test_missing_file(self, client):
        res = client.post(
            "/api/v1/documents/analyze",
            data={},
            content_type="multipart/form-data",
        )
        assert res.status_code == 400
        data = res.get_json()
        assert data["error"]["code"] == "MISSING_FILE"

    def test_unsupported_format(self, client):
        data = {
            "file": (io.BytesIO(b"fake word doc"), "test.docx"),
        }
        res = client.post(
            "/api/v1/documents/analyze",
            data=data,
            content_type="multipart/form-data",
        )
        assert res.status_code == 415
        data = res.get_json()
        assert data["error"]["code"] == "UNSUPPORTED_FORMAT"

    def test_empty_file_upload(self, client):
        data = {
            "file": (io.BytesIO(b""), "empty.txt"),
        }
        res = client.post(
            "/api/v1/documents/analyze",
            data=data,
            content_type="multipart/form-data",
        )
        assert res.status_code == 400
        data = res.get_json()
        assert data["error"]["code"] == "EMPTY_FILE"


class TestSearchEndpoint:
    """Tests for POST /api/v1/search."""

    def test_valid_search(self, client):
        payload = {
            "query": "consideration exchanged under agreement",
            "top_k": 2,
        }
        res = client.post("/api/v1/search", json=payload)
        assert res.status_code == 200
        data = res.get_json()
        assert data["query"] == payload["query"]
        assert len(data["results"]) > 0

        first = data["results"][0]
        assert "document_id" in first
        assert "document_name" in first
        assert "passage" in first
        assert "score" in first
        assert "score_method" in first
        assert first["score_method"] == "tfidf_lexical_wsd"
        assert "consideration" in first["matched_terms"]

    def test_missing_query(self, client):
        res = client.post("/api/v1/search", json={"top_k": 5})
        assert res.status_code == 400
        data = res.get_json()
        assert data["error"]["code"] == "MISSING_QUERY"

    def test_empty_query(self, client):
        res = client.post("/api/v1/search", json={"query": "   "})
        assert res.status_code == 400
        data = res.get_json()
        assert data["error"]["code"] == "MISSING_QUERY"

    def test_invalid_top_k(self, client):
        res = client.post("/api/v1/search", json={"query": "test", "top_k": -5})
        assert res.status_code == 400
        data = res.get_json()
        assert data["error"]["code"] == "INVALID_TOP_K"

    def test_no_match_returns_empty_results_and_warning(self, client):
        payload = {"query": "deepwater oil drilling offshore"}
        res = client.post("/api/v1/search", json=payload)
        assert res.status_code == 200
        data = res.get_json()
        assert data["results"] == []
        assert len(data["warnings"]) > 0


class TestApiHardeningAndSecurity:
    """Security and input hardening tests for Phase 4 verification."""

    def test_malformed_json_body(self, client):
        """Malformed JSON string should return 400 MALFORMED_JSON."""
        res = client.post(
            "/api/v1/analyze",
            data="{invalid_json_body: true",
            content_type="application/json",
        )
        assert res.status_code == 400
        data = res.get_json()
        assert data["error"]["code"] in ["MALFORMED_JSON", "INVALID_REQUEST"]

    def test_json_array_body(self, client):
        """Array payload should be rejected with 400 INVALID_BODY."""
        res = client.post(
            "/api/v1/analyze",
            data="[1, 2, 3]",
            content_type="application/json",
        )
        assert res.status_code == 400
        data = res.get_json()
        assert data["error"]["code"] == "INVALID_BODY"

    def test_secret_leakage_prevented(self, client, monkeypatch):
        """API endpoints must never leak API keys in response payloads."""
        secret_key = "gsk_test_secret_key_never_leak_xyz789"
        monkeypatch.setenv("GROQ_API_KEY", secret_key)
        monkeypatch.setenv("LEGAL_SENSE_ENABLE_LLM", "true")

        # Check /health
        health_res = client.get("/health")
        assert secret_key not in health_res.get_data(as_text=True)

        # Check /api/v1/analyze
        analyze_res = client.post(
            "/api/v1/analyze",
            json={"text": "Court ordered relief.", "use_llm": True},
        )
        assert secret_key not in analyze_res.get_data(as_text=True)

    def test_search_malformed_json(self, client):
        """Search endpoint should handle malformed JSON cleanly."""
        res = client.post(
            "/api/v1/search",
            data="not a json",
            content_type="application/json",
        )
        assert res.status_code == 400
        data = res.get_json()
        assert data["error"]["code"] in ["MALFORMED_JSON", "INVALID_REQUEST"]

    def test_empty_filename_upload(self, client):
        """Multipart upload with empty filename is rejected."""
        data = {
            "file": (io.BytesIO(b"some content"), ""),
        }
        res = client.post(
            "/api/v1/documents/analyze",
            data=data,
            content_type="multipart/form-data",
        )
        assert res.status_code == 400
        resp_data = res.get_json()
        assert resp_data["error"]["code"] == "EMPTY_FILENAME"

