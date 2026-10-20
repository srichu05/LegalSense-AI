"""Tests for the legal glossary module."""

import json
import os
import tempfile

import pytest

from legalsense.legal_glossary import (
    GlossaryLoadError,
    load_glossary,
    lookup_term,
    reset_cache,
)
from legalsense.schemas import LegalGlossaryEntry


@pytest.fixture(autouse=True)
def _reset_glossary_cache():
    """Reset the glossary cache before each test."""
    reset_cache()
    yield
    reset_cache()


def _write_temp_glossary(entries: list[dict]) -> str:
    """Write a temporary glossary JSON file and return its path."""
    fd, path = tempfile.mkstemp(suffix=".json")
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        json.dump(entries, f)
    return path


class TestLoadGlossary:
    """Tests for load_glossary()."""

    def test_load_valid_glossary(self):
        path = _write_temp_glossary([
            {"term": "consideration", "definition": "Something of value.", "source": "Test"},
            {"term": "appeal", "definition": "A higher court review.", "source": "Test"},
        ])
        try:
            glossary = load_glossary(path)
            assert len(glossary) == 2
            assert "consideration" in glossary
            assert "appeal" in glossary
        finally:
            os.unlink(path)

    def test_entries_are_legal_glossary_entries(self):
        path = _write_temp_glossary([
            {"term": "party", "definition": "A participant in a legal proceeding.", "source": "Test"},
        ])
        try:
            glossary = load_glossary(path)
            entry = glossary["party"]
            assert isinstance(entry, LegalGlossaryEntry)
            assert entry.term == "party"
            assert entry.definition == "A participant in a legal proceeding."
            assert entry.source == "Test"
        finally:
            os.unlink(path)

    def test_missing_file_raises_error(self):
        with pytest.raises(GlossaryLoadError, match="not found"):
            load_glossary("/nonexistent/path/glossary.json")

    def test_invalid_json_raises_error(self):
        fd, path = tempfile.mkstemp(suffix=".json")
        with os.fdopen(fd, "w") as f:
            f.write("{not valid json")
        try:
            with pytest.raises(GlossaryLoadError, match="Invalid JSON"):
                load_glossary(path)
        finally:
            os.unlink(path)

    def test_non_array_json_raises_error(self):
        fd, path = tempfile.mkstemp(suffix=".json")
        with os.fdopen(fd, "w") as f:
            json.dump({"term": "test"}, f)
        try:
            with pytest.raises(GlossaryLoadError, match="JSON array"):
                load_glossary(path)
        finally:
            os.unlink(path)

    def test_missing_term_skipped(self):
        path = _write_temp_glossary([
            {"definition": "No term here.", "source": "Test"},
            {"term": "valid", "definition": "A valid entry.", "source": "Test"},
        ])
        try:
            glossary = load_glossary(path)
            assert len(glossary) == 1
            assert "valid" in glossary
        finally:
            os.unlink(path)

    def test_missing_definition_skipped(self):
        path = _write_temp_glossary([
            {"term": "incomplete", "source": "Test"},
            {"term": "valid", "definition": "A valid entry.", "source": "Test"},
        ])
        try:
            glossary = load_glossary(path)
            assert len(glossary) == 1
        finally:
            os.unlink(path)

    def test_optional_metadata_fields(self):
        path = _write_temp_glossary([
            {
                "term": "suit",
                "definition": "A civil action.",
                "source": "Test",
                "jurisdiction": "Common law",
                "usage_example": "The company filed a suit.",
                "limitations": "Educational only.",
            },
        ])
        try:
            glossary = load_glossary(path)
            entry = glossary["suit"]
            assert entry.jurisdiction == "Common law"
            assert entry.usage_example == "The company filed a suit."
            assert entry.limitations == "Educational only."
        finally:
            os.unlink(path)

    def test_missing_optional_metadata_defaults_to_empty(self):
        path = _write_temp_glossary([
            {"term": "action", "definition": "A judicial proceeding."},
        ])
        try:
            glossary = load_glossary(path)
            entry = glossary["action"]
            assert entry.source == ""
            assert entry.jurisdiction == ""
            assert entry.usage_example == ""
            assert entry.limitations == ""
        finally:
            os.unlink(path)

    def test_case_insensitive_keys(self):
        path = _write_temp_glossary([
            {"term": "Consideration", "definition": "Test.", "source": "Test"},
        ])
        try:
            glossary = load_glossary(path)
            assert "consideration" in glossary
        finally:
            os.unlink(path)

    def test_caching(self):
        path = _write_temp_glossary([
            {"term": "test", "definition": "Test.", "source": "Test"},
        ])
        try:
            g1 = load_glossary(path)
            g2 = load_glossary(path)
            assert g1 is g2  # Same object due to caching
        finally:
            os.unlink(path)

    def test_force_reload(self):
        path = _write_temp_glossary([
            {"term": "test", "definition": "Version 1.", "source": "Test"},
        ])
        try:
            g1 = load_glossary(path)
            assert g1["test"].definition == "Version 1."

            # Overwrite with new content
            with open(path, "w", encoding="utf-8") as f:
                json.dump([{"term": "test", "definition": "Version 2.", "source": "Test"}], f)

            g2 = load_glossary(path, force_reload=True)
            assert g2["test"].definition == "Version 2."
        finally:
            os.unlink(path)


class TestLookupTerm:
    """Tests for lookup_term()."""

    def test_found_term(self):
        path = _write_temp_glossary([
            {"term": "consideration", "definition": "Something of value.", "source": "Test"},
        ])
        try:
            entry = lookup_term("consideration", path)
            assert entry is not None
            assert entry.term == "consideration"
        finally:
            os.unlink(path)

    def test_unknown_term(self):
        path = _write_temp_glossary([
            {"term": "consideration", "definition": "Something of value.", "source": "Test"},
        ])
        try:
            entry = lookup_term("xyzzy", path)
            assert entry is None
        finally:
            os.unlink(path)

    def test_case_insensitive_lookup(self):
        path = _write_temp_glossary([
            {"term": "Appeal", "definition": "A higher court review.", "source": "Test"},
        ])
        try:
            entry = lookup_term("APPEAL", path)
            assert entry is not None
        finally:
            os.unlink(path)


class TestGlossaryDistinctFromWordnet:
    """Verify that glossary entries are clearly separate from WordNet data."""

    def test_glossary_entry_has_no_synset_id(self):
        """LegalGlossaryEntry should not have a synset_id field."""
        entry = LegalGlossaryEntry(
            term="consideration",
            definition="Something of value.",
            source="Test",
        )
        assert not hasattr(entry, "synset_id")

    def test_glossary_entry_has_source_provenance(self):
        """Glossary entries should carry their own source."""
        path = _write_temp_glossary([
            {"term": "motion", "definition": "A formal court request.", "source": "Black's Law Dictionary"},
        ])
        try:
            entry = lookup_term("motion", path)
            assert entry.source == "Black's Law Dictionary"
        finally:
            os.unlink(path)


class TestDefaultGlossary:
    """Test loading the actual project glossary at data/legal_glossary.json."""

    def test_default_glossary_loads(self):
        """The default glossary should load without error."""
        glossary = load_glossary()
        assert len(glossary) >= 5, "Expected at least 5 terms in the default glossary"

    def test_default_glossary_has_expected_terms(self):
        """The default glossary should include key legal terms."""
        glossary = load_glossary()
        expected_terms = ["consideration", "execution", "party", "action", "suit"]
        for term in expected_terms:
            assert term in glossary, f"Expected '{term}' in the default glossary"
