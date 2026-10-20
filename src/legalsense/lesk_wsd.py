"""Extended Lesk WSD algorithm for LegalSense.

Implements an Extended Lesk baseline for Word Sense Disambiguation as
described in docs/WSD_DESIGN.md.

Algorithm overview:
1. Retrieve candidate WordNet senses for the target word.
2. Build a context representation from the surrounding sentence (lowercased
   lemmas of content tokens).
3. For each candidate sense, compute overlap between the context and:
   a. The candidate's gloss (definition) — weight 1.0
   b. The candidate's example sentences — weight 1.0
   c. Hypernym glosses — weight 0.5 (Extended Lesk extension)
   d. Hyponym glosses — weight 0.5 (Extended Lesk extension)
4. Rank candidates by total weighted overlap score.
5. Select the top candidate if its evidence is sufficient; mark as uncertain
   if scores are tied or below the minimum evidence threshold.

Scoring details:
- Overlap is measured as the count of shared word tokens (lowercased) between
  the context representation and the candidate's gloss/example/relation text.
- Each token is counted once per gloss component to avoid inflation.
- Scores are raw overlap counts, NOT calibrated probabilities.
- The minimum evidence threshold and tie margin are configurable.

Uncertainty rules:
- uncertain=True if: no candidates, all scores are 0, top two scores are
  tied or within the tie margin, or the top score is below the minimum
  evidence threshold.
- selected_sense=None if: no candidates or all scores are 0.
"""

from __future__ import annotations

import logging
from typing import Optional

from legalsense.preprocessing import (
    PreprocessedText,
    ProcessedToken,
    find_target_token,
    preprocess,
    tokenize_gloss,
)
from legalsense.schemas import (
    CandidateSense,
    EvidenceItem,
    LegalGlossaryEntry,
    WSDResult,
)
from legalsense.wordnet_service import (
    get_candidate_senses,
    get_related_glosses,
)

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Configurable scoring parameters
# ---------------------------------------------------------------------------
# These defaults are provisional. They should be validated on development
# data and may be adjusted. See docs/WSD_DESIGN.md § 4.

DEFAULT_MIN_EVIDENCE_SCORE: float = 1.0
"""Minimum overlap score to consider a selection non-trivial."""

DEFAULT_TIE_MARGIN: float = 0.5
"""If the gap between rank-1 and rank-2 is within this margin, mark as tied."""

DEFAULT_GLOSS_WEIGHT: float = 1.0
"""Weight for gloss (definition) overlap."""

DEFAULT_EXAMPLE_WEIGHT: float = 1.0
"""Weight for example sentence overlap."""

DEFAULT_HYPERNYM_WEIGHT: float = 0.5
"""Weight for hypernym gloss overlap (Extended Lesk extension)."""

DEFAULT_HYPONYM_WEIGHT: float = 0.5
"""Weight for hyponym gloss overlap (Extended Lesk extension)."""

DEFAULT_FILTER_STOPWORDS: bool = True
"""Whether to filter English function/stop words from overlap scoring to prevent spurious matches."""

try:
    from nltk.corpus import stopwords
    _STOPWORDS = set(stopwords.words("english"))
except Exception:
    _STOPWORDS = {
        "the", "a", "an", "in", "on", "at", "to", "for", "of", "with", "by", "from",
        "and", "or", "is", "are", "was", "were", "it", "this", "that", "be", "as",
        "have", "has", "had", "do", "does", "did", "but", "not", "so", "if", "out",
    }


def disambiguate(
    sentence: str,
    target_word: str,
    *,
    pos: Optional[str] = None,
    min_evidence_score: float = DEFAULT_MIN_EVIDENCE_SCORE,
    tie_margin: float = DEFAULT_TIE_MARGIN,
    gloss_weight: float = DEFAULT_GLOSS_WEIGHT,
    example_weight: float = DEFAULT_EXAMPLE_WEIGHT,
    hypernym_weight: float = DEFAULT_HYPERNYM_WEIGHT,
    hyponym_weight: float = DEFAULT_HYPONYM_WEIGHT,
    filter_stopwords: bool = DEFAULT_FILTER_STOPWORDS,
    legal_entry: Optional[LegalGlossaryEntry] = None,
) -> WSDResult:
    """Run Extended Lesk WSD on a target word within a sentence.

    Args:
        sentence: The full sentence or short text containing the target word.
        target_word: The word to disambiguate.
        pos: Optional POS override (NOUN, VERB, ADJ, ADV). If None, the POS
             is inferred from preprocessing.
        min_evidence_score: Minimum top score to consider non-trivial.
        tie_margin: Maximum gap between rank-1 and rank-2 to flag a tie.
        gloss_weight: Weight for gloss overlap.
        example_weight: Weight for example overlap.
        hypernym_weight: Weight for hypernym gloss overlap.
        hyponym_weight: Weight for hyponym gloss overlap.
        legal_entry: Optional legal glossary entry to attach (not mixed with
                     WordNet scoring).

    Returns:
        A WSDResult with ranked candidates, evidence and uncertainty status.
    """
    # 1. Preprocess the sentence
    preprocessed = preprocess(sentence)

    # 2. Find the target token in the preprocessed text
    target_token = find_target_token(preprocessed, target_word)
    detected_pos = pos or (target_token.pos if target_token else "UNKNOWN")
    detected_lemma = target_token.lemma if target_token else target_word.lower()

    # 3. Build context representation (lowercased lemmas, no punctuation)
    if filter_stopwords:
        context_words = set(t.lemma for t in preprocessed.content_tokens() if t.lemma.lower() not in _STOPWORDS and len(t.lemma) > 1)
    else:
        context_words = set(preprocessed.context_words())
    # Remove the target word itself from context to avoid trivial self-overlap
    context_words.discard(detected_lemma)

    def _filter_toks(tokens: list[str]) -> set[str]:
        if filter_stopwords:
            return set(w for w in tokens if w not in _STOPWORDS and len(w) > 1)
        return set(tokens)

    # 4. Retrieve candidates from WordNet
    effective_pos = detected_pos if detected_pos != "UNKNOWN" else None
    candidates = get_candidate_senses(
        word=target_word,
        pos=effective_pos,
        lemma=detected_lemma,
    )

    # Build provenance list
    provenance = ["wordnet"]
    if legal_entry:
        provenance.append("legal_glossary")

    # Handle no candidates
    if not candidates:
        return WSDResult(
            term=target_word,
            sentence=sentence,
            lemma=detected_lemma,
            pos=detected_pos,
            candidate_senses=[],
            selected_sense=None,
            selection_method="extended_lesk",
            evidence=[],
            uncertain=True,
            source_provenance=provenance,
            legal_glossary_entry=legal_entry,
        )

    # 5. Score each candidate
    all_evidence: list[EvidenceItem] = []

    for candidate in candidates:
        total_score = 0.0

        # 5a. Gloss overlap
        gloss_tokens = _filter_toks(tokenize_gloss(candidate.definition))
        gloss_overlap = context_words & gloss_tokens
        gloss_contribution = len(gloss_overlap) * gloss_weight
        total_score += gloss_contribution
        if gloss_overlap:
            all_evidence.append(EvidenceItem(
                candidate_synset_id=candidate.synset_id,
                overlap_tokens=sorted(gloss_overlap),
                overlap_source="gloss",
                contribution=gloss_contribution,
            ))

        # 5b. Example overlap
        example_overlap_all: set[str] = set()
        for example in candidate.examples:
            example_tokens = _filter_toks(tokenize_gloss(example))
            example_overlap_all |= (context_words & example_tokens)
        example_contribution = len(example_overlap_all) * example_weight
        total_score += example_contribution
        if example_overlap_all:
            all_evidence.append(EvidenceItem(
                candidate_synset_id=candidate.synset_id,
                overlap_tokens=sorted(example_overlap_all),
                overlap_source="examples",
                contribution=example_contribution,
            ))

        # 5c. Extended Lesk: hypernym and hyponym glosses
        related = get_related_glosses(candidate.synset_id)

        hypernym_overlap: set[str] = set()
        for gloss in related.get("hypernym_glosses", []):
            hypernym_overlap |= (context_words & _filter_toks(tokenize_gloss(gloss)))
        hyper_contribution = len(hypernym_overlap) * hypernym_weight
        total_score += hyper_contribution
        if hypernym_overlap:
            all_evidence.append(EvidenceItem(
                candidate_synset_id=candidate.synset_id,
                overlap_tokens=sorted(hypernym_overlap),
                overlap_source="hypernym_gloss",
                contribution=hyper_contribution,
            ))

        hyponym_overlap: set[str] = set()
        for gloss in related.get("hyponym_glosses", []):
            hyponym_overlap |= (context_words & _filter_toks(tokenize_gloss(gloss)))
        hypo_contribution = len(hyponym_overlap) * hyponym_weight
        total_score += hypo_contribution
        if hyponym_overlap:
            all_evidence.append(EvidenceItem(
                candidate_synset_id=candidate.synset_id,
                overlap_tokens=sorted(hyponym_overlap),
                overlap_source="hyponym_gloss",
                contribution=hypo_contribution,
            ))

        candidate.score = total_score

    # 6. Rank candidates by score (descending), break ties by synset_id
    candidates.sort(key=lambda c: (-c.score, c.synset_id))
    for rank, candidate in enumerate(candidates, start=1):
        candidate.rank = rank

    # 7. Determine selection and uncertainty
    top = candidates[0]
    runner_up_score = candidates[1].score if len(candidates) > 1 else -1.0

    all_zero = all(c.score == 0.0 for c in candidates)
    is_tied = (len(candidates) > 1
               and (top.score - runner_up_score) <= tie_margin)
    weak_evidence = top.score < min_evidence_score

    uncertain = all_zero or is_tied or weak_evidence

    selected = None if all_zero else top

    return WSDResult(
        term=target_word,
        sentence=sentence,
        lemma=detected_lemma,
        pos=detected_pos,
        candidate_senses=candidates,
        selected_sense=selected,
        selection_method="extended_lesk",
        evidence=all_evidence,
        uncertain=uncertain,
        source_provenance=provenance,
        legal_glossary_entry=legal_entry,
    )


def disambiguate_all_targets(
    sentence: str,
    target_words: list[str],
    **kwargs,
) -> list[WSDResult]:
    """Run disambiguation on multiple target words in the same sentence.

    Args:
        sentence: The input sentence.
        target_words: List of words to disambiguate.
        **kwargs: Additional arguments passed to disambiguate().

    Returns:
        A list of WSDResult objects, one per target word.
    """
    return [disambiguate(sentence, word, **kwargs) for word in target_words]
