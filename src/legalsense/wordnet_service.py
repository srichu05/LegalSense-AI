"""WordNet sense inventory service for LegalSense.

Retrieves candidate synsets, definitions, examples and lexical relations
from NLTK WordNet at runtime. No synset identifiers or definitions are
hardcoded — all data comes from the installed WordNet corpus.

Design:
- Independent of Flask; can be imported and unit-tested directly.
- POS filtering uses the standard WordNet POS characters (n, v, a, r).
- Missing examples or relations are represented as empty lists.
- Source provenance is always 'wordnet'.
"""

from __future__ import annotations

import logging
from typing import Optional

from nltk.corpus import wordnet as wn

from legalsense.schemas import CandidateSense

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# POS mapping: our labels -> WordNet POS characters
# ---------------------------------------------------------------------------
_WN_POS_MAP: dict[str, str] = {
    "NOUN": wn.NOUN,    # 'n'
    "VERB": wn.VERB,    # 'v'
    "ADJ": wn.ADJ,      # 'a'
    "ADV": wn.ADV,      # 'r'
}

_WN_POS_DISPLAY: dict[str, str] = {
    wn.NOUN: "NOUN",
    wn.VERB: "VERB",
    wn.ADJ: "ADJ",
    wn.ADJ_SAT: "ADJ",  # satellite adjectives map to ADJ
    wn.ADV: "ADV",
}


def ensure_wordnet() -> bool:
    """Check that WordNet data is available; download if missing.

    Returns True if WordNet is usable, False otherwise.
    """
    try:
        wn.synsets("test")
        return True
    except LookupError:
        import nltk
        logger.info("WordNet data not found. Downloading...")
        nltk.download("wordnet", quiet=True)
        try:
            wn.synsets("test")
            return True
        except LookupError:
            logger.error(
                "WordNet download failed. Install manually:\n"
                "  python -c \"import nltk; nltk.download('wordnet')\""
            )
            return False


def get_candidate_senses(
    word: str,
    pos: Optional[str] = None,
    lemma: Optional[str] = None,
) -> list[CandidateSense]:
    """Retrieve all WordNet candidate senses for a word.

    Args:
        word: The target word (surface form).
        pos: Optional POS label (NOUN, VERB, ADJ, ADV). If provided and
             mappable to a WordNet POS, only synsets matching that POS are
             returned. Unsupported POS values are ignored (all POS returned).
        lemma: Optional lemmatized form to use for lookup instead of *word*.

    Returns:
        A list of CandidateSense objects with data retrieved from WordNet.
        Returns an empty list if the word has no synsets.
    """
    lookup = (lemma or word).lower().replace(" ", "_")

    # Determine WordNet POS filter
    wn_pos = _WN_POS_MAP.get(pos) if pos else None

    if wn_pos:
        synsets = wn.synsets(lookup, pos=wn_pos)
    else:
        synsets = wn.synsets(lookup)

    if not synsets:
        logger.debug("No WordNet synsets found for '%s' (pos=%s).", lookup, pos)
        return []

    candidates: list[CandidateSense] = []
    seen: set[str] = set()  # deduplicate by synset name

    for ss in synsets:
        sid = ss.name()
        if sid in seen:
            continue
        seen.add(sid)

        candidates.append(CandidateSense(
            synset_id=sid,
            definition=ss.definition(),
            pos=_WN_POS_DISPLAY.get(ss.pos(), "UNKNOWN"),
            examples=list(ss.examples()),
            lemma_names=_deduplicated_lemma_names(ss, lookup),
            hypernyms=[h.name() for h in ss.hypernyms()],
            hyponyms=[h.name() for h in ss.hyponyms()],
            source="wordnet",
        ))

    return candidates


def _deduplicated_lemma_names(synset, lookup_word: str) -> list[str]:
    """Return unique lemma names for a synset, excluding the lookup word itself."""
    names: list[str] = []
    seen: set[str] = set()
    for lemma in synset.lemmas():
        name = lemma.name().replace("_", " ")
        lower = name.lower()
        if lower not in seen and lower != lookup_word:
            seen.add(lower)
            names.append(name)
    return names


def get_synset_gloss(synset_id: str) -> str:
    """Get the gloss/definition for a synset by its ID.

    Returns an empty string if the synset is not found.
    """
    ss = wn.synset(synset_id)
    return ss.definition() if ss else ""


def get_related_glosses(synset_id: str) -> dict[str, list[str]]:
    """Get glosses of related synsets (hypernyms, hyponyms) for Extended Lesk.

    Returns a dict mapping relation type to a list of gloss strings.
    """
    try:
        ss = wn.synset(synset_id)
    except Exception:
        return {}

    result: dict[str, list[str]] = {
        "hypernym_glosses": [],
        "hyponym_glosses": [],
    }

    for h in ss.hypernyms():
        result["hypernym_glosses"].append(h.definition())
    for h in ss.hyponyms():
        result["hyponym_glosses"].append(h.definition())

    return result
