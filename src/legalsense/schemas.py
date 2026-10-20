"""Structured result types for the LegalSense WSD engine.

These dataclasses define the output contract described in docs/WSD_DESIGN.md § 7.
They are designed for future JSON serialization by Flask without modification.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field, asdict
from typing import Optional


@dataclass
class CandidateSense:
    """A single WordNet candidate sense with lexical relations."""

    synset_id: str
    """WordNet synset identifier, e.g. 'party.n.01'."""

    definition: str
    """Gloss/definition from WordNet."""

    pos: str
    """Part-of-speech tag (NOUN, VERB, ADJ, ADV)."""

    examples: list[str] = field(default_factory=list)
    """Example sentences from WordNet, if any."""

    lemma_names: list[str] = field(default_factory=list)
    """Synonym lemma names within the synset."""

    hypernyms: list[str] = field(default_factory=list)
    """Hypernym synset IDs, if available."""

    hyponyms: list[str] = field(default_factory=list)
    """Hyponym synset IDs, if available."""

    score: float = 0.0
    """Overlap score from Lesk/Extended Lesk. Not a calibrated probability."""

    rank: int = 0
    """Rank among candidates (1 = highest score)."""

    source: str = "wordnet"
    """Provenance: always 'wordnet' for this class."""


@dataclass
class EvidenceItem:
    """One piece of scoring evidence linking context to a candidate."""

    candidate_synset_id: str
    """Which candidate this evidence supports."""

    overlap_tokens: list[str]
    """Tokens that overlapped between context and candidate gloss/examples."""

    overlap_source: str
    """Where the overlap was found: 'gloss', 'examples', 'hypernym_gloss', etc."""

    contribution: float
    """Score contribution from this evidence source."""


@dataclass
class LegalGlossaryEntry:
    """A curated legal glossary entry, distinct from WordNet data."""

    term: str
    """The legal term."""

    definition: str
    """Domain-specific definition."""

    source: str
    """Provenance/citation for the definition."""

    jurisdiction: str = ""
    """Jurisdiction or scope, if applicable."""

    usage_example: str = ""
    """A short illustrative example."""

    limitations: str = ""
    """Known limitations or caveats about this definition."""


@dataclass
class WSDResult:
    """Complete WSD analysis result for a target word in context.

    This is the primary output structure of the LegalSense WSD engine.
    See docs/WSD_DESIGN.md § 7 for the output contract.
    """

    term: str
    """The original target word as it appears in the input."""

    sentence: str
    """The sentence or context in which the term was analyzed."""

    lemma: str
    """Lemmatized form of the target word."""

    pos: str
    """Part-of-speech of the target word (NOUN, VERB, ADJ, ADV, or UNKNOWN)."""

    candidate_senses: list[CandidateSense] = field(default_factory=list)
    """All WordNet candidate senses, ranked by score."""

    selected_sense: Optional[CandidateSense] = None
    """The top-ranked candidate, or None if evidence is insufficient."""

    selection_method: str = "extended_lesk"
    """Algorithm used for disambiguation."""

    evidence: list[EvidenceItem] = field(default_factory=list)
    """Detailed scoring evidence for each candidate."""

    uncertain: bool = True
    """True if the selection has weak evidence, a tie, or no candidates."""

    source_provenance: list[str] = field(default_factory=list)
    """Data sources consulted: 'wordnet', 'legal_glossary', etc."""

    legal_glossary_entry: Optional[LegalGlossaryEntry] = None
    """Matching legal glossary entry, if any. Separate from WordNet data."""

    def to_dict(self) -> dict:
        """Serialize to a plain dictionary suitable for JSON."""
        return asdict(self)

    def to_json(self, indent: int = 2) -> str:
        """Serialize to a JSON string."""
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False)
