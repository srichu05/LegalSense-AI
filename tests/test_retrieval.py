"""Tests for the lightweight passage retrieval module."""

import pytest

from legalsense.retrieval import PassageRetriever, SearchResult
from legalsense.segmentation import Passage


@pytest.fixture
def sample_passages():
    """Create a diverse set of legal passages for testing retrieval."""
    return [
        Passage(
            passage_id="doc_contract_p001",
            document_id="doc_contract",
            document_name="contract.txt",
            text="The parties agreed that consideration shall be paid in full prior to execution.",
            page=1,
        ),
        Passage(
            passage_id="doc_contract_p002",
            document_id="doc_contract",
            document_name="contract.txt",
            text="Any finance charge or late fee shall accrue at the rate of five percent per annum.",
            page=2,
        ),
        Passage(
            passage_id="doc_ruling_p001",
            document_id="doc_ruling",
            document_name="ruling.txt",
            text="The appellant filed a formal appeal in the appellate court seeking injunctive relief.",
            page=1,
        ),
        Passage(
            passage_id="doc_ruling_p002",
            document_id="doc_ruling",
            document_name="ruling.txt",
            text="The trial judge dismissed the action after hearing oral arguments on the defense motion.",
            page=2,
        ),
    ]


class TestPassageRetriever:
    """Tests for PassageRetriever."""

    def test_empty_collection(self):
        retriever = PassageRetriever([])
        results = retriever.search("consideration contract")
        assert results == []

    def test_empty_query(self, sample_passages):
        retriever = PassageRetriever(sample_passages)
        assert retriever.search("") == []
        assert retriever.search("   ") == []

    def test_no_match_query(self, sample_passages):
        retriever = PassageRetriever(sample_passages)
        results = retriever.search("submarine astronaut telescope")
        assert results == []

    def test_relevant_ranking(self, sample_passages):
        retriever = PassageRetriever(sample_passages)
        results = retriever.search("consideration paid under contract", top_k=2)

        assert len(results) > 0
        top = results[0]
        assert isinstance(top, SearchResult)
        assert top.document_id == "doc_contract"
        assert top.passage_id == "doc_contract_p001"
        assert "consideration" in top.matched_terms
        assert top.score > 0.0

    def test_legal_ruling_search(self, sample_passages):
        retriever = PassageRetriever(sample_passages)
        results = retriever.search("appeal in appellate court seeking relief", top_k=2)

        assert len(results) > 0
        top = results[0]
        assert top.document_id == "doc_ruling"
        assert top.passage_id == "doc_ruling_p001"
        assert "appeal" in top.matched_terms

    def test_top_k_clamping(self, sample_passages):
        retriever = PassageRetriever(sample_passages)
        results = retriever.search("the court", top_k=1)
        assert len(results) <= 1

        results_many = retriever.search("the court", top_k=100)
        assert len(results_many) <= len(sample_passages)

    def test_metadata_preservation(self, sample_passages):
        retriever = PassageRetriever(sample_passages)
        results = retriever.search("consideration", top_k=1)

        assert len(results) == 1
        res = results[0]
        assert res.document_id == "doc_contract"
        assert res.document_name == "contract.txt"
        assert res.page == 1
        assert res.score_method == "tfidf_lexical_wsd"

    def test_to_dict_schema(self, sample_passages):
        """to_dict() must conform strictly to docs/API_SPEC.md § 4."""
        retriever = PassageRetriever(sample_passages)
        results = retriever.search("consideration", top_k=1)
        d = results[0].to_dict()

        assert "document_id" in d
        assert "document_name" in d
        assert "page" in d
        assert "passage" in d
        assert "score" in d
        assert "score_method" in d
        assert "matched_terms" in d
        assert isinstance(d["score"], float)

    def test_deterministic_ranking(self, sample_passages):
        retriever = PassageRetriever(sample_passages)
        r1 = retriever.search("court action motion", top_k=3)
        r2 = retriever.search("court action motion", top_k=3)

        assert len(r1) == len(r2)
        for a, b in zip(r1, r2):
            assert a.passage_id == b.passage_id
            assert a.score == b.score
