"""Tests for the passage segmentation module."""

import pytest

from legalsense.document_ingestion import ExtractedPage, IngestedDocument
from legalsense.segmentation import (
    Passage,
    segment_document,
    segment_text,
    split_into_sentences,
)


class TestSentenceSplitting:
    """Tests for split_into_sentences()."""

    def test_empty_string(self):
        assert split_into_sentences("") == []

    def test_whitespace_only(self):
        assert split_into_sentences("   \n\t  ") == []

    def test_single_sentence(self):
        text = "This is a single legal clause."
        sentences = split_into_sentences(text)
        assert len(sentences) == 1
        s_text, start, end = sentences[0]
        assert s_text == text
        assert text[start:end] == text

    def test_multiple_sentences_with_offsets(self):
        text = "The first party agreed. The second party disagreed."
        sentences = split_into_sentences(text)
        assert len(sentences) == 2
        for s_text, start, end in sentences:
            assert text[start:end] == s_text


class TestSegmentText:
    """Tests for segment_text()."""

    def test_empty_input(self):
        assert segment_text("") == []

    def test_whitespace_only(self):
        assert segment_text("   \n\n  ") == []

    def test_single_short_passage(self):
        text = "The court issued an interlocutory injunction pending trial."
        passages = segment_text(
            text,
            document_id="doc_test_1",
            document_name="injunction.txt",
            page=1,
        )
        assert len(passages) == 1
        p = passages[0]
        assert isinstance(p, Passage)
        assert p.document_id == "doc_test_1"
        assert p.document_name == "injunction.txt"
        assert p.page == 1
        assert p.passage_id == "doc_test_1_p001"
        assert p.text == text
        assert p.word_count == len(text.split())

    def test_sentence_boundary_preservation(self):
        """Passages must not be cut in the middle of sentences."""
        sentences = [
            "Section 1 defines the parties and their legal capacity.",
            "Section 2 sets forth the consideration exchanged between the parties.",
            "Section 3 specifies the governing law of the commercial agreement.",
            "Section 4 establishes exclusive forum jurisdiction in the superior court.",
        ]
        text = " ".join(sentences)

        # Set target_words small to force splitting into multiple passages
        passages = segment_text(text, target_words=15, max_words=25)
        assert len(passages) >= 2

        # Verify that each passage ends with sentence-ending punctuation
        for p in passages:
            assert p.text.endswith(".")
            # Ensure each passage text consists of complete sentences from the original list
            assert any(s in p.text for s in sentences)

    def test_deterministic_output(self):
        """Identical input produces identical passage boundaries and IDs."""
        text = "First clause here. Second clause there. Third clause elsewhere."
        passages1 = segment_text(text, document_id="doc_det", document_name="det.txt")
        passages2 = segment_text(text, document_id="doc_det", document_name="det.txt")

        assert len(passages1) == len(passages2)
        for p1, p2 in zip(passages1, passages2):
            assert p1.passage_id == p2.passage_id
            assert p1.text == p2.text
            assert p1.start_char == p2.start_char
            assert p1.end_char == p2.end_char

    def test_page_metadata_preserved(self):
        """Page metadata is retained on each generated passage."""
        text = "This is a statement on page four."
        passages = segment_text(text, page=4)
        assert len(passages) == 1
        assert passages[0].page == 4


class TestSegmentDocument:
    """Tests for segment_document()."""

    def test_multi_page_document(self):
        doc = IngestedDocument(
            document_id="doc_pages",
            filename="agreement.pdf",
            file_type="pdf",
            pages=[
                ExtractedPage(page_number=1, text="Page one text regarding consideration."),
                ExtractedPage(page_number=2, text="Page two text regarding contract execution."),
            ],
            full_text="Page one text regarding consideration.\n\nPage two text regarding contract execution.",
            total_characters=78,
        )

        passages = segment_document(doc)
        assert len(passages) == 2
        assert passages[0].page == 1
        assert passages[0].passage_id == "doc_pages_p001"
        assert "consideration" in passages[0].text

        assert passages[1].page == 2
        assert passages[1].passage_id == "doc_pages_p002"
        assert "execution" in passages[1].text

    def test_document_with_empty_page(self):
        doc = IngestedDocument(
            document_id="doc_empty_p",
            filename="blank.pdf",
            file_type="pdf",
            pages=[
                ExtractedPage(page_number=1, text="Page one text."),
                ExtractedPage(page_number=2, text="   "),  # Empty
                ExtractedPage(page_number=3, text="Page three text."),
            ],
        )
        passages = segment_document(doc)
        assert len(passages) == 2
        pages = [p.page for p in passages]
        assert pages == [1, 3]
