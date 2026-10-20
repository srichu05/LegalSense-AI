"""Passage segmentation module for LegalSense.

Segments legal text and ingested documents into coherent, sentence-respecting
passages while preserving document identifiers, page numbers, character offsets,
and source provenance. Deterministic and lightweight.
"""

from __future__ import annotations

import logging
import re
from dataclasses import asdict, dataclass
from typing import Optional

from legalsense.document_ingestion import IngestedDocument

logger = logging.getLogger(__name__)

# Default target word count per passage
DEFAULT_TARGET_WORDS = 150
DEFAULT_MIN_WORDS = 20
DEFAULT_MAX_WORDS = 300


@dataclass
class Passage:
    """A segmented passage with source and position metadata."""

    passage_id: str
    """Deterministic identifier, e.g. 'doc_123456_p001'."""

    document_id: str
    """Identifier of the originating document."""

    document_name: str
    """Original filename or title of the document."""

    text: str
    """Normalized passage text."""

    page: Optional[int] = None
    """1-indexed page number if originating from a paged document (e.g. PDF)."""

    start_char: int = 0
    """Start character offset within the source page or document."""

    end_char: int = 0
    """End character offset within the source page or document."""

    word_count: int = 0
    """Number of words in the passage."""

    def __post_init__(self):
        if not self.word_count and self.text:
            self.word_count = len(self.text.split())

    def to_dict(self) -> dict:
        """Serialize to a plain dictionary for API responses."""
        return asdict(self)


def split_into_sentences(text: str) -> list[tuple[str, int, int]]:
    """Split text into sentences, returning list of (sentence_text, start_offset, end_offset).

    Uses NLTK sent_tokenize if available with fallback to regex sentence splitting.
    Preserves exact character offsets.
    """
    if not text or not text.strip():
        return []

    # Regex sentence boundary finder that preserves offsets:
    # Looks for sentence-ending punctuation (.!?) followed by whitespace and capital letter/digit
    # Also handles paragraph boundaries (\n\n)
    pattern = re.compile(r"([^\n\r]+?[\.\?\!](?=\s+[A-Z0-9\"'\(]|$)|[^\n\r]+(?=\n\n|$))", re.MULTILINE)
    matches = list(pattern.finditer(text))

    sentences: list[tuple[str, int, int]] = []
    if matches:
        for m in matches:
            s_text = m.group(0).strip()
            if s_text:
                # Find trimmed offsets
                start = m.start() + m.group(0).find(s_text)
                end = start + len(s_text)
                sentences.append((s_text, start, end))

    # If regex found nothing (e.g. no punctuation, or single line), return whole text
    if not sentences:
        s_text = text.strip()
        start = text.find(s_text)
        end = start + len(s_text)
        sentences.append((s_text, start, end))

    return sentences


def segment_text(
    text: str,
    document_id: str = "doc_text",
    document_name: str = "input_text",
    page: Optional[int] = None,
    target_words: int = DEFAULT_TARGET_WORDS,
    max_words: int = DEFAULT_MAX_WORDS,
) -> list[Passage]:
    """Segment a block of text into coherent passages.

    Groups sentences together up to approximately target_words without splitting
    sentences mid-way.

    Args:
        text: Input text to segment.
        document_id: Internal document identifier.
        document_name: Original document name.
        page: Optional page number.
        target_words: Desired approximate word count per passage.
        max_words: Hard upper word count limit per passage.

    Returns:
        A list of Passage objects.
    """
    if not text or not text.strip():
        return []

    sentences = split_into_sentences(text)
    if not sentences:
        return []

    passages: list[Passage] = []
    current_sentences: list[str] = []
    current_start = -1
    current_end = -1
    current_word_count = 0
    passage_index = 1

    for s_text, s_start, s_end in sentences:
        s_words = len(s_text.split())

        # If adding this sentence exceeds max_words and we already have content, flush
        if current_sentences and (current_word_count + s_words > max_words or current_word_count >= target_words):
            p_text = " ".join(current_sentences)
            passages.append(Passage(
                passage_id=f"{document_id}_p{passage_index:03d}",
                document_id=document_id,
                document_name=document_name,
                text=p_text,
                page=page,
                start_char=current_start,
                end_char=current_end,
                word_count=current_word_count,
            ))
            passage_index += 1
            current_sentences = []
            current_start = -1
            current_end = -1
            current_word_count = 0

        if not current_sentences:
            current_start = s_start
        current_sentences.append(s_text)
        current_end = s_end
        current_word_count += s_words

    # Flush remaining sentences
    if current_sentences:
        p_text = " ".join(current_sentences)
        passages.append(Passage(
            passage_id=f"{document_id}_p{passage_index:03d}",
            document_id=document_id,
            document_name=document_name,
            text=p_text,
            page=page,
            start_char=current_start,
            end_char=current_end,
            word_count=current_word_count,
        ))

    return passages


def segment_document(
    document: IngestedDocument,
    target_words: int = DEFAULT_TARGET_WORDS,
) -> list[Passage]:
    """Segment an IngestedDocument into passages preserving page boundaries.

    Each page is segmented individually so passage metadata accurately reflects
    the page number from which it came.

    Args:
        document: IngestedDocument instance.
        target_words: Desired approximate word count per passage.

    Returns:
        List of Passage objects across the entire document.
    """
    all_passages: list[Passage] = []
    global_index = 1

    for page in document.pages:
        if not page.text.strip():
            continue
        page_passages = segment_text(
            text=page.text,
            document_id=document.document_id,
            document_name=document.filename,
            page=page.page_number if document.file_type == "pdf" else None,
            target_words=target_words,
        )
        for p in page_passages:
            # Re-index passage_id globally across the document
            p.passage_id = f"{document.document_id}_p{global_index:03d}"
            all_passages.append(p)
            global_index += 1

    return all_passages
