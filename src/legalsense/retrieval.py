"""Lightweight passage retrieval module for LegalSense.

Combines TF-IDF relevance, lexical keyword matching, and legal glossary / WSD signals.
Deterministic, explainable, and lightweight for local execution and Render deployment
without requiring transformer models or GPU.
"""

from __future__ import annotations

import logging
import re
from dataclasses import asdict, dataclass, field
from typing import Optional

from legalsense.legal_glossary import load_glossary
from legalsense.preprocessing import tokenize_gloss
from legalsense.segmentation import Passage

logger = logging.getLogger(__name__)


@dataclass
class SearchResult:
    """A ranked passage retrieval result matching docs/API_SPEC.md § 4."""

    document_id: str
    """Originating document ID."""

    document_name: str
    """Filename or title of the document."""

    passage: str
    """Excerpt text of the matching passage."""

    score: float = 0.0
    """Combined relevance score (raw score, NOT a calibrated probability)."""

    score_method: str = "tfidf_lexical_wsd"
    """Scoring method descriptor."""

    matched_terms: list[str] = field(default_factory=list)
    """Query terms found in the passage."""

    page: Optional[int] = None
    """Page number if available."""

    passage_id: Optional[str] = None
    """Passage identifier."""

    tfidf_score: float = 0.0
    """TF-IDF cosine similarity component."""

    lexical_score: float = 0.0
    """Lexical match score component."""

    wsd_boost: float = 0.0
    """WSD / legal glossary boost component."""

    def to_dict(self) -> dict:
        """Format as dictionary strictly conforming to API_SPEC.md § 4."""
        return {
            "document_id": self.document_id,
            "document_name": self.document_name,
            "page": self.page,
            "passage": self.passage,
            "score": round(self.score, 4),
            "score_method": self.score_method,
            "matched_terms": self.matched_terms,
        }


class PassageRetriever:
    """In-memory indexer and retriever for legal text passages."""

    def __init__(
        self,
        passages: Optional[list[Passage]] = None,
        tfidf_weight: float = 0.6,
        lexical_weight: float = 0.3,
        wsd_boost_weight: float = 0.1,
    ):
        self.passages: list[Passage] = []
        self.tfidf_weight = tfidf_weight
        self.lexical_weight = lexical_weight
        self.wsd_boost_weight = wsd_boost_weight

        self._vectorizer = None
        self._tfidf_matrix = None
        self._glossary_terms: set[str] = set()

        # Load glossary terms for domain boosting
        try:
            glossary = load_glossary()
            self._glossary_terms = set(glossary.keys())
        except Exception:
            self._glossary_terms = set()

        if passages:
            self.index_passages(passages)

    def index_passages(self, passages: list[Passage]) -> None:
        """Index a collection of passages using scikit-learn TfidfVectorizer."""
        self.passages = list(passages)
        if not self.passages:
            self._vectorizer = None
            self._tfidf_matrix = None
            return

        from sklearn.feature_extraction.text import TfidfVectorizer

        corpus_texts = [p.text for p in self.passages]
        self._vectorizer = TfidfVectorizer(
            lowercase=True,
            stop_words="english",
            sublinear_tf=True,
            token_pattern=r"(?u)\b\w+\b",
        )
        try:
            self._tfidf_matrix = self._vectorizer.fit_transform(corpus_texts)
        except ValueError:
            # Empty vocabulary (e.g. only stop words or symbols)
            self._vectorizer = None
            self._tfidf_matrix = None

    def search(
        self,
        query: str,
        top_k: int = 5,
        min_score: float = 0.0,
    ) -> list[SearchResult]:
        """Rank passages against a user query using TF-IDF + lexical + legal glossary matching.

        Args:
            query: User search query string.
            top_k: Maximum number of results to return (clamped >= 1).
            min_score: Minimum total score threshold.

        Returns:
            Ranked list of SearchResult objects, sorted by score descending.
        """
        top_k = max(1, min(top_k, 100))

        if not query or not query.strip() or not self.passages:
            return []

        clean_query = query.strip()
        query_tokens = set(tokenize_gloss(clean_query))
        if not query_tokens:
            return []

        # 1. Compute TF-IDF similarities
        tfidf_scores = [0.0] * len(self.passages)
        if self._vectorizer is not None and self._tfidf_matrix is not None:
            from sklearn.metrics.pairwise import cosine_similarity

            try:
                query_vec = self._vectorizer.transform([clean_query])
                sims = cosine_similarity(query_vec, self._tfidf_matrix).flatten()
                tfidf_scores = [float(s) for s in sims]
            except Exception as exc:
                logger.warning("TF-IDF scoring failed for query '%s': %s", clean_query, exc)
                tfidf_scores = [0.0] * len(self.passages)

        # 2. Score each passage with lexical overlap & legal glossary boost
        results: list[SearchResult] = []

        for idx, passage in enumerate(self.passages):
            passage_tokens = set(tokenize_gloss(passage.text))
            matched = sorted(query_tokens & passage_tokens)

            # Lexical score: Jaccard-like ratio of matched query tokens
            lex_score = len(matched) / len(query_tokens) if query_tokens else 0.0

            # Domain / WSD boost: does the query or passage contain curated legal glossary terms?
            matched_legal_terms = query_tokens & passage_tokens & self._glossary_terms
            domain_boost = min(1.0, 0.5 * len(matched_legal_terms))

            raw_tfidf = tfidf_scores[idx] if idx < len(tfidf_scores) else 0.0

            # Combined weighted score
            total_score = (
                self.tfidf_weight * raw_tfidf
                + self.lexical_weight * lex_score
                + self.wsd_boost_weight * domain_boost
            )

            if total_score > min_score or (matched and min_score == 0.0):
                results.append(SearchResult(
                    document_id=passage.document_id,
                    document_name=passage.document_name,
                    passage=passage.text,
                    score=total_score,
                    score_method="tfidf_lexical_wsd",
                    matched_terms=matched,
                    page=passage.page,
                    passage_id=passage.passage_id,
                    tfidf_score=raw_tfidf,
                    lexical_score=lex_score,
                    wsd_boost=domain_boost,
                ))

        # 3. Deterministic sort: descending by score, tie-break by document_id and passage_id
        results.sort(
            key=lambda r: (-r.score, r.document_id, r.passage_id or "")
        )

        return results[:top_k]
