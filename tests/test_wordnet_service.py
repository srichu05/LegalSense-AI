"""Tests for the WordNet service module."""

import pytest
from nltk.corpus import wordnet as wn

from legalsense.wordnet_service import (
    ensure_wordnet,
    get_candidate_senses,
    get_related_glosses,
    get_synset_gloss,
)


@pytest.fixture(autouse=True)
def _ensure_wordnet_available():
    """Ensure WordNet data is available before every test."""
    assert ensure_wordnet(), (
        "WordNet data is not available. Run:\n"
        "  python -c \"import nltk; nltk.download('wordnet')\""
    )


class TestGetCandidateSenses:
    """Tests for get_candidate_senses()."""

    def test_known_word_has_synsets(self):
        """A common English word should have at least one synset."""
        candidates = get_candidate_senses("bank")
        assert len(candidates) > 0

    def test_multiple_senses(self):
        """An ambiguous word like 'bank' should have multiple senses."""
        candidates = get_candidate_senses("bank")
        assert len(candidates) >= 2, "Expected 'bank' to have multiple senses"

    def test_synset_ids_from_wordnet(self):
        """Synset IDs should be real WordNet synset names."""
        candidates = get_candidate_senses("party")
        for c in candidates:
            # Verify each synset_id is a valid WordNet synset
            ss = wn.synset(c.synset_id)
            assert ss is not None
            assert c.synset_id == ss.name()

    def test_definitions_from_wordnet(self):
        """Definitions should match what WordNet returns."""
        candidates = get_candidate_senses("party")
        for c in candidates:
            ss = wn.synset(c.synset_id)
            assert c.definition == ss.definition()

    def test_no_synsets_for_nonsense_word(self):
        """A made-up word should return no candidates."""
        candidates = get_candidate_senses("xyzzyplugh")
        assert candidates == []

    def test_pos_filtering_noun(self):
        """POS filtering should restrict results to the specified POS."""
        all_senses = get_candidate_senses("run")
        noun_senses = get_candidate_senses("run", pos="NOUN")
        verb_senses = get_candidate_senses("run", pos="VERB")

        assert len(all_senses) >= len(noun_senses)
        assert all(c.pos == "NOUN" for c in noun_senses)
        assert all(c.pos == "VERB" for c in verb_senses)

    def test_unsupported_pos_returns_all(self):
        """An unsupported POS value should not filter (return all senses)."""
        all_senses = get_candidate_senses("action")
        unknown_pos_senses = get_candidate_senses("action", pos="INTERJECTION")
        assert len(unknown_pos_senses) == len(all_senses)

    def test_examples_are_lists(self):
        """Examples should be lists (possibly empty)."""
        candidates = get_candidate_senses("court")
        for c in candidates:
            assert isinstance(c.examples, list)

    def test_missing_relations_are_empty_lists(self):
        """Hypernyms and hyponyms should be empty lists when unavailable."""
        candidates = get_candidate_senses("the")  # Likely few/no useful relations
        for c in candidates:
            assert isinstance(c.hypernyms, list)
            assert isinstance(c.hyponyms, list)

    def test_source_provenance_is_wordnet(self):
        """All candidates should have source='wordnet'."""
        candidates = get_candidate_senses("contract")
        for c in candidates:
            assert c.source == "wordnet"

    def test_lemma_names_excludes_target(self):
        """Lemma names should not include the lookup word itself."""
        candidates = get_candidate_senses("party")
        for c in candidates:
            assert "party" not in [n.lower() for n in c.lemma_names]

    def test_lemma_lookup(self):
        """Using the lemma parameter should look up by lemma."""
        by_word = get_candidate_senses("parties")
        by_lemma = get_candidate_senses("parties", lemma="party")
        # Lemma lookup should find more senses (or at least the same)
        assert len(by_lemma) >= len(by_word)


class TestGetSynsetGloss:
    """Tests for get_synset_gloss()."""

    def test_valid_synset(self):
        """A valid synset ID should return its definition."""
        synsets = wn.synsets("dog")
        if synsets:
            gloss = get_synset_gloss(synsets[0].name())
            assert gloss == synsets[0].definition()

    def test_matches_wordnet(self):
        """The gloss should match what WordNet returns directly."""
        ss = wn.synsets("court", pos=wn.NOUN)
        if ss:
            assert get_synset_gloss(ss[0].name()) == ss[0].definition()


class TestGetRelatedGlosses:
    """Tests for get_related_glosses()."""

    def test_returns_dict(self):
        """Should return a dict with hypernym and hyponym gloss lists."""
        synsets = wn.synsets("dog", pos=wn.NOUN)
        if synsets:
            related = get_related_glosses(synsets[0].name())
            assert "hypernym_glosses" in related
            assert "hyponym_glosses" in related
            assert isinstance(related["hypernym_glosses"], list)
            assert isinstance(related["hyponym_glosses"], list)

    def test_invalid_synset_returns_empty(self):
        """An invalid synset ID should return an empty dict."""
        related = get_related_glosses("not_a_real_synset.n.99")
        assert related == {}

    def test_hypernyms_match_wordnet(self):
        """Hypernym glosses should match what WordNet returns."""
        synsets = wn.synsets("dog", pos=wn.NOUN)
        if synsets:
            ss = synsets[0]
            related = get_related_glosses(ss.name())
            expected_hypernym_glosses = [h.definition() for h in ss.hypernyms()]
            assert related["hypernym_glosses"] == expected_hypernym_glosses
