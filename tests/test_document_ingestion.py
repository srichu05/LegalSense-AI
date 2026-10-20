"""Tests for document ingestion and validation."""

import io
import tempfile
from pathlib import Path

import pytest

from legalsense.document_ingestion import (
    DocumentValidationError,
    IngestedDocument,
    ingest_document,
    normalize_document_text,
    sanitize_filename,
)


class TestFilenameSanitization:
    """Tests for sanitize_filename()."""

    def test_standard_filename(self):
        assert sanitize_filename("contract.txt") == "contract.txt"

    def test_strips_directory_traversal(self):
        assert sanitize_filename("../../etc/passwd.txt") == "passwd.txt"
        assert sanitize_filename("C:\\Windows\\System32\\legal.pdf") == "legal.pdf"

    def test_empty_or_none(self):
        assert sanitize_filename("") == "unnamed_document"
        assert sanitize_filename(None) == "unnamed_document"


class TestTextNormalization:
    """Tests for normalize_document_text()."""

    def test_crlf_normalized(self):
        text = "Clause 1\r\nClause 2\r\nClause 3"
        normalized = normalize_document_text(text)
        assert "\r" not in normalized
        assert "Clause 1\nClause 2\nClause 3" == normalized

    def test_whitespace_and_tabs_collapsed(self):
        text = "Party   A \t\t and   Party B"
        normalized = normalize_document_text(text)
        assert normalized == "Party A and Party B"

    def test_excessive_newlines_collapsed(self):
        text = "Paragraph 1\n\n\n\n\nParagraph 2"
        normalized = normalize_document_text(text)
        assert normalized == "Paragraph 1\n\nParagraph 2"

    def test_punctuation_and_sentence_boundaries_preserved(self):
        text = "The court ruled in favor of Plaintiff. However, damages were limited."
        normalized = normalize_document_text(text)
        assert normalized == text


class TestIngestTxt:
    """Tests for ingesting TXT documents."""

    def test_valid_txt_from_bytes(self):
        content = b"The parties entered into an agreement regarding consideration."
        doc = ingest_document(content, filename="test_agreement.txt")

        assert isinstance(doc, IngestedDocument)
        assert doc.filename == "test_agreement.txt"
        assert doc.file_type == "txt"
        assert doc.document_id.startswith("doc_")
        assert len(doc.pages) == 1
        assert doc.pages[0].page_number == 1
        assert doc.pages[0].text == content.decode("utf-8")
        assert doc.total_characters == len(content)
        assert doc.is_scanned_or_empty is False
        assert doc.warnings == []

    def test_valid_txt_from_stream(self):
        stream = io.BytesIO(b"Section 1: Representations and Warranties.")
        stream.filename = "warranties.txt"
        doc = ingest_document(stream)

        assert doc.filename == "warranties.txt"
        assert "Representations" in doc.full_text

    def test_valid_txt_from_file_path(self):
        with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False, encoding="utf-8") as f:
            f.write("A formal legal instrument executed under seal.")
            temp_path = f.name

        try:
            doc = ingest_document(temp_path)
            assert doc.filename == Path(temp_path).name
            assert "executed under seal" in doc.full_text
        finally:
            Path(temp_path).unlink(missing_ok=True)

    def test_empty_file_raises_error(self):
        with pytest.raises(DocumentValidationError, match="empty") as exc_info:
            ingest_document(b"", filename="empty.txt")
        assert exc_info.value.code == "EMPTY_FILE"

    def test_whitespace_only_raises_error(self):
        with pytest.raises(DocumentValidationError, match="whitespace") as exc_info:
            ingest_document(b"   \n\t   ", filename="blank.txt")
        assert exc_info.value.code == "EMPTY_CONTENT"

    def test_oversized_file_raises_error(self):
        content = b"x" * 1024
        # Enforce 500 byte limit
        with pytest.raises(DocumentValidationError, match="exceeds limit") as exc_info:
            ingest_document(content, filename="large.txt", max_bytes=500)
        assert exc_info.value.code == "FILE_TOO_LARGE"

    def test_unsupported_format_raises_error(self):
        with pytest.raises(DocumentValidationError, match="Unsupported file extension") as exc_info:
            ingest_document(b"fake docx content", filename="contract.docx")
        assert exc_info.value.code == "UNSUPPORTED_FORMAT"

    def test_missing_file_raises_error(self):
        with pytest.raises(DocumentValidationError, match="File not found") as exc_info:
            ingest_document("/nonexistent/path/to/missing.txt")
        assert exc_info.value.code == "FILE_NOT_FOUND"


class TestIngestPdf:
    """Tests for PDF ingestion with PyMuPDF."""

    def test_pdf_parsing_if_pymupdf_available(self):
        try:
            import fitz
        except ImportError:
            pytest.skip("PyMuPDF not yet installed; skipping real PDF generation test.")

        # Create a small valid PDF in memory using fitz
        doc_mem = fitz.open()
        page1 = doc_mem.new_page()
        page1.insert_text((50, 50), "Page 1: In the Supreme Court of Appeals. The petitioner filed a suit.")
        page2 = doc_mem.new_page()
        page2.insert_text((50, 50), "Page 2: The court granted equitable relief to the plaintiff.")
        pdf_bytes = doc_mem.tobytes()
        doc_mem.close()

        ingested = ingest_document(pdf_bytes, filename="court_record.pdf")
        assert ingested.file_type == "pdf"
        assert len(ingested.pages) == 2
        assert ingested.pages[0].page_number == 1
        assert "Supreme Court" in ingested.pages[0].text
        assert ingested.pages[1].page_number == 2
        assert "equitable relief" in ingested.pages[1].text
        assert ingested.is_scanned_or_empty is False

    def test_scanned_pdf_detection(self):
        """A PDF with pages but zero extractable text must be flagged with a warning."""
        try:
            import fitz
        except ImportError:
            pytest.skip("PyMuPDF not yet installed; skipping scanned PDF test.")

        # Create a PDF with blank pages (simulating a scanned image without OCR)
        doc_mem = fitz.open()
        doc_mem.new_page()
        pdf_bytes = doc_mem.tobytes()
        doc_mem.close()

        ingested = ingest_document(pdf_bytes, filename="scanned_scan.pdf")
        assert ingested.is_scanned_or_empty is True
        assert any("OCR is not supported" in w for w in ingested.warnings)

    def test_corrupt_pdf_raises_error(self):
        try:
            import fitz
        except ImportError:
            pytest.skip("PyMuPDF not yet installed; skipping corrupt PDF test.")

        corrupt_bytes = b"%PDF-1.4 corrupt data not a real pdf content"
        with pytest.raises(DocumentValidationError) as exc_info:
            ingest_document(corrupt_bytes, filename="corrupt.pdf")
        assert exc_info.value.code in ["CORRUPT_PDF", "EMPTY_PDF"]
