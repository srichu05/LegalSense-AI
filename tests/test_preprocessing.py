"""Tests for the preprocessing module."""

import pytest
from legalsense.preprocessing import (
    PreprocessedText,
    ProcessedToken,
    find_target_token,
    preprocess,
    tokenize_gloss,
)


class TestPreprocess:
    """Tests for the preprocess() function."""

    def test_empty_string(self):
        result = preprocess("")
        assert result.original_text == ""
        assert result.tokens == []

    def test_whitespace_only(self):
        result = preprocess("   ")
        assert result.tokens == []

    def test_punctuation_only(self):
        result = preprocess("... !!! ???")
        assert all(t.is_punctuation for t in result.tokens)
        assert result.content_tokens() == []
        assert result.context_words() == []

    def test_basic_sentence(self):
        result = preprocess("The cat sat on the mat.")
        assert result.original_text == "The cat sat on the mat."
        content = result.content_tokens()
        assert len(content) >= 5  # at least the meaningful words
        # Original form should be preserved somewhere
        originals = [t.original for t in result.tokens]
        assert "The" in originals or "the" in originals

    def test_capitalization_preserved_in_original(self):
        result = preprocess("HELLO World")
        originals = [t.original for t in result.tokens]
        assert "HELLO" in originals
        assert "World" in originals

    def test_lowercase_in_lower_field(self):
        result = preprocess("HELLO World")
        lowers = [t.lower for t in result.tokens]
        assert "hello" in lowers
        assert "world" in lowers

    def test_lemmatization_running(self):
        result = preprocess("The dogs are running quickly.")
        lemmas = [t.lemma for t in result.content_tokens()]
        # "dogs" should lemmatize to "dog"
        assert "dog" in lemmas

    def test_pos_tagging_assigns_values(self):
        result = preprocess("The judge issued a ruling.")
        content = result.content_tokens()
        pos_values = {t.pos for t in content}
        # Should have at least one recognized POS
        assert pos_values - {"UNKNOWN"}, "Expected at least one non-UNKNOWN POS tag"

    def test_context_words_returns_lemmas(self):
        result = preprocess("The parties signed contracts.")
        words = result.context_words()
        assert all(isinstance(w, str) for w in words)
        assert all(w == w.lower() for w in words)

    def test_mixed_punctuation_and_words(self):
        result = preprocess("Hello, world!")
        content = result.content_tokens()
        assert len(content) >= 2
        assert "," not in [t.original for t in content]
        assert "!" not in [t.original for t in content]


class TestFindTargetToken:
    """Tests for find_target_token()."""

    def test_finds_by_lemma(self):
        preprocessed = preprocess("The parties provided consideration.")
        token = find_target_token(preprocessed, "consideration")
        assert token is not None
        assert token.lemma == "consideration"

    def test_finds_inflected_form(self):
        preprocessed = preprocess("The dogs barked loudly.")
        token = find_target_token(preprocessed, "dog")
        assert token is not None

    def test_case_insensitive(self):
        preprocessed = preprocess("The Judge ruled.")
        token = find_target_token(preprocessed, "judge")
        assert token is not None

    def test_returns_none_for_missing_word(self):
        preprocessed = preprocess("The cat sat on the mat.")
        token = find_target_token(preprocessed, "elephant")
        assert token is None

    def test_returns_none_for_empty_text(self):
        preprocessed = preprocess("")
        token = find_target_token(preprocessed, "anything")
        assert token is None


class TestTokenizeGloss:
    """Tests for tokenize_gloss()."""

    def test_basic_gloss(self):
        tokens = tokenize_gloss("a formal legal document")
        assert "formal" in tokens
        assert "legal" in tokens
        assert "document" in tokens

    def test_empty_string(self):
        assert tokenize_gloss("") == []

    def test_lowercased(self):
        tokens = tokenize_gloss("The Quick Brown Fox")
        assert all(t == t.lower() for t in tokens)

    def test_punctuation_removed(self):
        tokens = tokenize_gloss("something; or other (maybe).")
        assert ";" not in tokens
        assert "(" not in tokens
        assert ")" not in tokens
        assert "." not in tokens
