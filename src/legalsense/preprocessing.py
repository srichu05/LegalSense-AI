"""Text preprocessing for the LegalSense WSD engine.

Provides tokenization, lemmatization, POS tagging and context preparation.
Uses spaCy when a model is available; falls back to NLTK otherwise.

Design notes:
- Lowercasing is applied for scoring/overlap but original text is preserved.
- Stop words are NOT stripped by default because legal context words (e.g.
  "the", "under", "by") may carry meaningful overlap signal in Lesk scoring.
- Punctuation-only tokens are removed from scoring representations.
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from typing import Optional

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# POS mapping: Penn Treebank / spaCy coarse -> WordNet-compatible labels
# ---------------------------------------------------------------------------
_SPACY_POS_MAP: dict[str, str] = {
    "NOUN": "NOUN",
    "VERB": "VERB",
    "ADJ": "ADJ",
    "ADV": "ADV",
    "PROPN": "NOUN",  # proper nouns treated as nouns for WordNet
}

_NLTK_POS_MAP: dict[str, str] = {
    "NN": "NOUN", "NNS": "NOUN", "NNP": "NOUN", "NNPS": "NOUN",
    "VB": "VERB", "VBD": "VERB", "VBG": "VERB", "VBN": "VERB",
    "VBP": "VERB", "VBZ": "VERB",
    "JJ": "ADJ", "JJR": "ADJ", "JJS": "ADJ",
    "RB": "ADV", "RBR": "ADV", "RBS": "ADV",
}


@dataclass
class ProcessedToken:
    """A single preprocessed token with its linguistic annotations."""

    original: str
    """Original surface form."""

    lower: str
    """Lowercased form used for overlap scoring."""

    lemma: str
    """Lemmatized form."""

    pos: str
    """Coarse POS tag: NOUN, VERB, ADJ, ADV, or UNKNOWN."""

    is_punctuation: bool = False
    """True if the token consists entirely of punctuation."""

    is_stop: bool = False
    """True if the token is a stop word (informational; not removed)."""


@dataclass
class PreprocessedText:
    """Result of preprocessing a sentence or text fragment."""

    original_text: str
    """The input text exactly as provided."""

    tokens: list[ProcessedToken] = field(default_factory=list)
    """All tokens with annotations."""

    def content_tokens(self) -> list[ProcessedToken]:
        """Return tokens that are not pure punctuation."""
        return [t for t in self.tokens if not t.is_punctuation]

    def context_words(self) -> list[str]:
        """Return lowercased lemmas of content tokens for overlap scoring."""
        return [t.lemma for t in self.content_tokens()]


# ---------------------------------------------------------------------------
# Backend selection: spaCy preferred, NLTK fallback
# ---------------------------------------------------------------------------
_nlp = None  # spaCy model, loaded lazily
_backend: str = "none"


def _load_spacy() -> bool:
    """Attempt to load the spaCy English model."""
    global _nlp, _backend
    if _nlp is not None:
        return True
    try:
        import spacy
        _nlp = spacy.load("en_core_web_sm")
        _backend = "spacy"
        logger.info("spaCy en_core_web_sm loaded successfully.")
        return True
    except (ImportError, OSError) as exc:
        logger.warning(
            "spaCy model 'en_core_web_sm' not available (%s). "
            "Falling back to NLTK for tokenization/POS tagging. "
            "Install with: python -m spacy download en_core_web_sm",
            exc,
        )
        return False


def _ensure_nltk_resources() -> None:
    """Download NLTK resources if missing."""
    import nltk
    for resource in ["punkt_tab", "averaged_perceptron_tagger_eng", "wordnet"]:
        try:
            nltk.data.find(f"tokenizers/{resource}" if "punkt" in resource else resource)
        except LookupError:
            nltk.download(resource, quiet=True)


def _init_backend() -> None:
    """Initialize the best available NLP backend."""
    global _backend
    if _backend != "none":
        return
    if not _load_spacy():
        _ensure_nltk_resources()
        _backend = "nltk"
        logger.info("Using NLTK fallback for preprocessing.")


def get_backend() -> str:
    """Return the active preprocessing backend name."""
    _init_backend()
    return _backend


# ---------------------------------------------------------------------------
# Core preprocessing
# ---------------------------------------------------------------------------

def preprocess(text: str) -> PreprocessedText:
    """Tokenize, lemmatize and POS-tag the input text.

    Args:
        text: Raw input sentence or short text.

    Returns:
        A PreprocessedText object with annotated tokens.
    """
    _init_backend()
    result = PreprocessedText(original_text=text)

    if not text or not text.strip():
        return result

    if _backend == "spacy" and _nlp is not None:
        result.tokens = _preprocess_spacy(text)
    else:
        result.tokens = _preprocess_nltk(text)

    return result


def _preprocess_spacy(text: str) -> list[ProcessedToken]:
    """Preprocess using spaCy."""
    doc = _nlp(text)
    tokens = []
    for tok in doc:
        is_punct = tok.is_punct or bool(re.fullmatch(r"[^\w]+", tok.text))
        pos = _SPACY_POS_MAP.get(tok.pos_, "UNKNOWN")
        tokens.append(ProcessedToken(
            original=tok.text,
            lower=tok.lower_,
            lemma=tok.lemma_.lower(),
            pos=pos,
            is_punctuation=is_punct,
            is_stop=tok.is_stop,
        ))
    return tokens


def _preprocess_nltk(text: str) -> list[ProcessedToken]:
    """Preprocess using NLTK as a fallback."""
    import nltk
    from nltk.stem import WordNetLemmatizer

    _ensure_nltk_resources()

    words = nltk.word_tokenize(text)
    tagged = nltk.pos_tag(words)
    lemmatizer = WordNetLemmatizer()

    # NLTK stop words (loaded once)
    try:
        nltk.data.find("corpora/stopwords")
    except LookupError:
        nltk.download("stopwords", quiet=True)
    from nltk.corpus import stopwords
    stop_set = set(stopwords.words("english"))

    tokens = []
    for word, tag in tagged:
        is_punct = bool(re.fullmatch(r"[^\w]+", word))
        pos = _NLTK_POS_MAP.get(tag, "UNKNOWN")

        # Lemmatize using the mapped WordNet POS
        wn_pos = _pos_to_wordnet_char(pos)
        lemma = lemmatizer.lemmatize(word.lower(), pos=wn_pos) if wn_pos else word.lower()

        tokens.append(ProcessedToken(
            original=word,
            lower=word.lower(),
            lemma=lemma,
            pos=pos,
            is_punctuation=is_punct,
            is_stop=word.lower() in stop_set,
        ))
    return tokens


def _pos_to_wordnet_char(pos: str) -> Optional[str]:
    """Map our POS labels to WordNet single-character POS for lemmatization."""
    return {"NOUN": "n", "VERB": "v", "ADJ": "a", "ADV": "r"}.get(pos)


# ---------------------------------------------------------------------------
# Utility functions
# ---------------------------------------------------------------------------

def find_target_token(
    preprocessed: PreprocessedText,
    target_word: str,
) -> Optional[ProcessedToken]:
    """Find the best matching token for a target word in preprocessed text.

    Matches by lemma first, then by lowercased form.
    Returns None if no match is found.
    """
    target_lower = target_word.lower()

    # Prefer exact lemma match among content tokens
    for tok in preprocessed.content_tokens():
        if tok.lemma == target_lower:
            return tok

    # Fall back to lowercased surface match
    for tok in preprocessed.content_tokens():
        if tok.lower == target_lower:
            return tok

    return None


def tokenize_gloss(text: str) -> list[str]:
    """Tokenize and normalize a gloss or example for overlap scoring.

    Returns lowercased content tokens (no punctuation).
    Uses simple whitespace/regex tokenization to avoid backend overhead.
    """
    if not text:
        return []
    # Simple word tokenization: split on non-alphanumeric
    words = re.findall(r"[a-zA-Z0-9]+", text.lower())
    return words
