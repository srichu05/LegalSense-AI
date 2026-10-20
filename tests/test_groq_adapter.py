"""Tests for the optional Groq contextual assistance adapter."""

import json
from unittest.mock import MagicMock, patch

import pytest

from legalsense.groq_adapter import (
    LLMAssistanceResult,
    is_llm_enabled,
    query_groq_wsd_assistance,
)
from legalsense.schemas import CandidateSense


@pytest.fixture
def sample_candidates():
    return [
        CandidateSense(
            synset_id="consideration.n.01",
            definition="The process of giving careful thought to something.",
            pos="NOUN",
        ),
        CandidateSense(
            synset_id="consideration.n.02",
            definition="A fee charged for an exchange; compensation.",
            pos="NOUN",
        ),
    ]


class TestGroqAdapterWithoutKey:
    """Tests when GROQ_API_KEY is not configured or disabled."""

    def test_disabled_by_default_without_key(self, monkeypatch):
        monkeypatch.delenv("GROQ_API_KEY", raising=False)
        assert is_llm_enabled() is False

        res = query_groq_wsd_assistance(
            "The parties exchanged consideration.",
            "consideration",
            [],
        )
        assert res.status == "disabled"
        assert "GROQ_API_KEY is not set" in (res.warning or "")

    def test_disabled_via_feature_flag(self, monkeypatch):
        monkeypatch.setenv("GROQ_API_KEY", "gsk_test_mock_key")
        monkeypatch.setenv("LEGAL_SENSE_ENABLE_LLM", "false")
        assert is_llm_enabled() is False

        res = query_groq_wsd_assistance(
            "The parties exchanged consideration.",
            "consideration",
            [],
        )
        assert res.status == "disabled"

    def test_empty_candidates_returns_unavailable(self, monkeypatch):
        monkeypatch.setenv("GROQ_API_KEY", "gsk_test_mock_key")
        monkeypatch.setenv("LEGAL_SENSE_ENABLE_LLM", "true")

        res = query_groq_wsd_assistance(
            "The parties exchanged consideration.",
            "consideration",
            [],
        )
        assert res.status == "unavailable"


class TestGroqAdapterValidationAndMocking:
    """Tests for strict validation of Groq responses."""

    def test_valid_synset_accepted(self, monkeypatch, sample_candidates):
        monkeypatch.setenv("GROQ_API_KEY", "gsk_test_mock_key")
        monkeypatch.setenv("LEGAL_SENSE_ENABLE_LLM", "true")

        mock_payload = {
            "choices": [
                {
                    "message": {
                        "content": json.dumps({
                            "selected_synset_id": "consideration.n.02",
                            "rationale": "Used in commercial exchange context.",
                        })
                    }
                }
            ]
        }
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps(mock_payload).encode("utf-8")
        mock_response.__enter__.return_value = mock_response

        with patch("urllib.request.urlopen", return_value=mock_response):
            res = query_groq_wsd_assistance(
                "The parties exchanged consideration under contract.",
                "consideration",
                sample_candidates,
            )
            assert res.status == "success"
            assert res.suggested_synset_id == "consideration.n.02"
            assert "commercial exchange" in (res.rationale or "")

    def test_hallucinated_synset_strictly_rejected(self, monkeypatch, sample_candidates):
        """If the LLM returns an invented synset ID not in candidates, it must be rejected."""
        monkeypatch.setenv("GROQ_API_KEY", "gsk_test_mock_key")
        monkeypatch.setenv("LEGAL_SENSE_ENABLE_LLM", "true")

        mock_payload = {
            "choices": [
                {
                    "message": {
                        "content": json.dumps({
                            "selected_synset_id": "invented_synset.n.99",
                            "rationale": "This seems legal.",
                        })
                    }
                }
            ]
        }
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps(mock_payload).encode("utf-8")
        mock_response.__enter__.return_value = mock_response

        with patch("urllib.request.urlopen", return_value=mock_response):
            res = query_groq_wsd_assistance(
                "The parties exchanged consideration under contract.",
                "consideration",
                sample_candidates,
            )
            assert res.status == "failed"
            assert res.suggested_synset_id is None
            assert "not in candidate senses" in (res.warning or "")

    def test_abstention_accepted(self, monkeypatch, sample_candidates):
        """When LLM returns 'NONE', it cleanly abstains."""
        monkeypatch.setenv("GROQ_API_KEY", "gsk_test_mock_key")
        monkeypatch.setenv("LEGAL_SENSE_ENABLE_LLM", "true")

        mock_payload = {
            "choices": [
                {
                    "message": {
                        "content": json.dumps({
                            "selected_synset_id": "NONE",
                            "rationale": "Legal definition applies instead.",
                        })
                    }
                }
            ]
        }
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps(mock_payload).encode("utf-8")
        mock_response.__enter__.return_value = mock_response

        with patch("urllib.request.urlopen", return_value=mock_response):
            res = query_groq_wsd_assistance(
                "Context text.",
                "word",
                sample_candidates,
            )
            assert res.status == "success"
            assert res.suggested_synset_id is None

    def test_network_timeout_gracefully_handled(self, monkeypatch, sample_candidates):
        import urllib.error

        monkeypatch.setenv("GROQ_API_KEY", "gsk_test_mock_key")
        monkeypatch.setenv("LEGAL_SENSE_ENABLE_LLM", "true")

        with patch("urllib.request.urlopen", side_effect=urllib.error.URLError("timed out")):
            res = query_groq_wsd_assistance(
                "Context text.",
                "word",
                sample_candidates,
            )
            assert res.status == "unavailable"
            assert "unavailable or timed out" in (res.warning or "")
