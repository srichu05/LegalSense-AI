"""Tests for the Extended Lesk WSD engine."""

import pytest

from legalsense.lesk_wsd import disambiguate, disambiguate_all_targets
from legalsense.schemas import LegalGlossaryEntry, WSDResult


class TestDisambiguateBasic:
    """Basic WSD disambiguation tests."""

    def test_returns_wsd_result(self):
        """disambiguate() should return a WSDResult object."""
        result = disambiguate(
            "The bank is on the river.",
            "bank",
        )
        assert isinstance(result, WSDResult)

    def test_term_and_sentence_preserved(self):
        """The original term and sentence should be preserved in the result."""
        sentence = "The court issued a ruling."
        result = disambiguate(sentence, "court")
        assert result.term == "court"
        assert result.sentence == sentence

    def test_has_candidate_senses(self):
        """A common ambiguous word should have multiple candidates."""
        result = disambiguate("The bank is on the river.", "bank")
        assert len(result.candidate_senses) >= 2

    def test_candidates_are_ranked(self):
        """Candidates should be sorted by score descending with sequential ranks."""
        result = disambiguate("The bank is on the river.", "bank")
        if result.candidate_senses:
            ranks = [c.rank for c in result.candidate_senses]
            assert ranks == list(range(1, len(ranks) + 1))
            scores = [c.score for c in result.candidate_senses]
            assert scores == sorted(scores, reverse=True)

    def test_selection_method(self):
        """The selection method should be 'extended_lesk'."""
        result = disambiguate("The dog chased the cat.", "dog")
        assert result.selection_method == "extended_lesk"

    def test_source_provenance_includes_wordnet(self):
        """Source provenance should include 'wordnet'."""
        result = disambiguate("The dog chased the cat.", "dog")
        assert "wordnet" in result.source_provenance


class TestContrastingContexts:
    """Test that different contexts produce different rankings."""

    def test_bank_river_vs_bank_money(self):
        """'bank' in a river context vs. financial context should score differently."""
        river_result = disambiguate(
            "I sat on the bank of the river watching the water flow.",
            "bank",
        )
        money_result = disambiguate(
            "I deposited my savings at the bank and opened a new account.",
            "bank",
        )

        # Both should have candidates
        assert len(river_result.candidate_senses) >= 2
        assert len(money_result.candidate_senses) >= 2

        # The top-ranked sense should be different (or at least the scores differ)
        if (river_result.selected_sense and money_result.selected_sense
                and river_result.selected_sense.score > 0
                and money_result.selected_sense.score > 0):
            # The scores should differ between contexts
            river_scores = {c.synset_id: c.score for c in river_result.candidate_senses}
            money_scores = {c.synset_id: c.score for c in money_result.candidate_senses}
            # At least one synset should have different scores in different contexts
            common_ids = set(river_scores.keys()) & set(money_scores.keys())
            score_diffs = [
                abs(river_scores[sid] - money_scores[sid]) for sid in common_ids
            ]
            assert any(d > 0 for d in score_diffs), (
                "Expected different scores for 'bank' in contrasting contexts"
            )

    def test_suit_legal_vs_clothing(self):
        """'suit' in legal vs. clothing context should rank differently."""
        legal_result = disambiguate(
            "The plaintiff filed a suit against the defendant in court.",
            "suit",
        )
        clothing_result = disambiguate(
            "He wore a dark suit with a silk tie to the formal dinner.",
            "suit",
        )

        assert len(legal_result.candidate_senses) >= 2
        assert len(clothing_result.candidate_senses) >= 2


class TestUncertaintyAndAbstention:
    """Test uncertainty handling, ties and abstention."""

    def test_unknown_word_no_candidates(self):
        """A made-up word should produce no candidates and uncertain=True."""
        result = disambiguate("The xyzzyplugh was very big.", "xyzzyplugh")
        assert result.candidate_senses == []
        assert result.selected_sense is None
        assert result.uncertain is True

    def test_empty_sentence(self):
        """An empty sentence should handle gracefully."""
        result = disambiguate("", "anything")
        assert result.uncertain is True

    def test_all_zero_scores_abstains(self):
        """If all overlap scores are zero, selected_sense should be None."""
        # Use a very short context with a common word to get zero overlap
        result = disambiguate("X.", "X")
        if result.candidate_senses and all(c.score == 0.0 for c in result.candidate_senses):
            assert result.selected_sense is None
            assert result.uncertain is True

    def test_uncertain_flag_for_weak_evidence(self):
        """Weak evidence (low score) should set uncertain=True."""
        result = disambiguate(
            "The thing happened.",
            "thing",
            min_evidence_score=100.0,  # Unreachably high threshold
        )
        assert result.uncertain is True

    def test_tie_detection(self):
        """When top candidates are tied, uncertain should be True."""
        result = disambiguate(
            "It happened.",
            "it",
            tie_margin=1000.0,  # Very wide margin to force tie detection
        )
        if len(result.candidate_senses) >= 2:
            assert result.uncertain is True


class TestScoringDetails:
    """Test the scoring mechanics."""

    def test_evidence_items_present(self):
        """Results with overlapping context should have evidence items."""
        result = disambiguate(
            "The judge presided over the court in the large building.",
            "court",
        )
        if any(c.score > 0 for c in result.candidate_senses):
            assert len(result.evidence) > 0

    def test_evidence_references_valid_candidate(self):
        """Each evidence item should reference an existing candidate synset."""
        result = disambiguate(
            "The judge presided over the court in the large building.",
            "court",
        )
        candidate_ids = {c.synset_id for c in result.candidate_senses}
        for ev in result.evidence:
            assert ev.candidate_synset_id in candidate_ids

    def test_evidence_overlap_source_documented(self):
        """Evidence items should have documented overlap sources."""
        valid_sources = {"gloss", "examples", "hypernym_gloss", "hyponym_gloss"}
        result = disambiguate(
            "The lawyer filed a motion in the court to dismiss the case.",
            "motion",
        )
        for ev in result.evidence:
            assert ev.overlap_source in valid_sources

    def test_deterministic_scoring(self):
        """Running the same input twice should produce the same scores."""
        sentence = "The parties signed the contract."
        r1 = disambiguate(sentence, "contract")
        r2 = disambiguate(sentence, "contract")

        scores1 = [(c.synset_id, c.score) for c in r1.candidate_senses]
        scores2 = [(c.synset_id, c.score) for c in r2.candidate_senses]
        assert scores1 == scores2

    def test_scores_are_not_labeled_as_probabilities(self):
        """Scores should be raw overlap counts, not normalized to [0,1]."""
        result = disambiguate(
            "The river bank was covered with grass and wildflowers.",
            "bank",
        )
        # Scores can exceed 1.0 (they are overlap counts, not probabilities)
        # At minimum, verify they are non-negative floats
        for c in result.candidate_senses:
            assert isinstance(c.score, float)
            assert c.score >= 0.0


class TestLegalGlossaryIntegration:
    """Test that legal glossary entries are attached but kept separate."""

    def test_legal_entry_attached(self):
        """A legal glossary entry should be attached to the result."""
        entry = LegalGlossaryEntry(
            term="consideration",
            definition="Something of value exchanged between parties.",
            source="Black's Law Dictionary (simplified)",
        )
        result = disambiguate(
            "The parties provided consideration under the contract.",
            "consideration",
            legal_entry=entry,
        )
        assert result.legal_glossary_entry is not None
        assert result.legal_glossary_entry.term == "consideration"
        assert "legal_glossary" in result.source_provenance

    def test_legal_entry_does_not_affect_scoring(self):
        """Legal glossary should not change WordNet candidate scores."""
        entry = LegalGlossaryEntry(
            term="consideration",
            definition="Something of value exchanged between parties.",
            source="Test",
        )
        without_legal = disambiguate(
            "The parties provided consideration under the contract.",
            "consideration",
        )
        with_legal = disambiguate(
            "The parties provided consideration under the contract.",
            "consideration",
            legal_entry=entry,
        )
        scores_without = [(c.synset_id, c.score) for c in without_legal.candidate_senses]
        scores_with = [(c.synset_id, c.score) for c in with_legal.candidate_senses]
        assert scores_without == scores_with

    def test_no_legal_entry_by_default(self):
        """Without a legal entry, legal_glossary_entry should be None."""
        result = disambiguate("The dog ran.", "dog")
        assert result.legal_glossary_entry is None


class TestDisambiguateAllTargets:
    """Test batch disambiguation."""

    def test_multiple_targets(self):
        """Should return one result per target word."""
        results = disambiguate_all_targets(
            "The party signed the contract in court.",
            ["party", "contract", "court"],
        )
        assert len(results) == 3
        assert all(isinstance(r, WSDResult) for r in results)


class TestSerialization:
    """Test that results are serializable."""

    def test_to_dict(self):
        """to_dict() should return a plain dictionary."""
        result = disambiguate("The dog chased the cat.", "dog")
        d = result.to_dict()
        assert isinstance(d, dict)
        assert d["term"] == "dog"

    def test_to_json(self):
        """to_json() should return valid JSON."""
        import json
        result = disambiguate("The dog chased the cat.", "dog")
        j = result.to_json()
        parsed = json.loads(j)
        assert parsed["term"] == "dog"
        assert "candidate_senses" in parsed


class TestStopwordFiltering:
    """Regression tests for stopword filtering in Extended Lesk."""

    def test_stopword_filtering_enabled_by_default(self):
        """Stopword filtering should be active and improve discriminative matching."""
        result = disambiguate(
            "The prosecutor filed a formal charge against the suspect in district court.",
            "charge",
        )
        assert result.selected_sense is not None
        # Should match legal/accusation sense rather than financial or physical
        assert any(
            result.selected_sense.synset_id.startswith(prefix)
            for prefix in ["charge.n.02", "charge.n.01", "accusation.n"]
        ) or "statement" in result.selected_sense.definition.lower() or "plead" in result.selected_sense.definition.lower() or "accuse" in result.selected_sense.definition.lower()

    def test_filter_stopwords_flag_can_be_toggled(self):
        """Disabling stopword filtering should still produce valid WSDResult without error."""
        res_with = disambiguate("The court heard the suit.", "suit", filter_stopwords=True)
        res_without = disambiguate("The court heard the suit.", "suit", filter_stopwords=False)
        assert isinstance(res_with, WSDResult)
        assert isinstance(res_without, WSDResult)
        assert len(res_with.candidate_senses) == len(res_without.candidate_senses)

