"""Document ingestion and validation for LegalSense.

Supports plain-text (.txt) and PDF (.pdf) files via PyMuPDF (fitz).
Extracts text page-by-page, retains page metadata, normalizes text
safely for downstream WSD, and enforces size and format limits.
"""

from __future__ import annotations

import io
import logging
import os
import re
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import BinaryIO, Optional, Union

logger = logging.getLogger(__name__)

# Default max upload size: 5 MB (can be overridden by env var)
DEFAULT_MAX_UPLOAD_MB = 5.0


def get_max_upload_bytes() -> int:
    """Return the configured maximum upload size in bytes."""
    env_val = os.getenv("LEGAL_SENSE_MAX_UPLOAD_MB")
    if env_val:
        try:
            return int(float(env_val) * 1024 * 1024)
        except ValueError:
            pass
    return int(DEFAULT_MAX_UPLOAD_MB * 1024 * 1024)


class DocumentValidationError(Exception):
    """Raised when an uploaded or ingested document fails validation."""

    def __init__(self, message: str, code: str = "INVALID_DOCUMENT"):
        super().__init__(message)
        self.message = message
        self.code = code


@dataclass
class ExtractedPage:
    """Page-level extraction result."""

    page_number: int
    """1-indexed page number."""

    text: str
    """Extracted and normalized text of the page."""

    char_count: int = 0
    """Character count of the page text."""

    def __post_init__(self):
        self.char_count = len(self.text)


@dataclass
class IngestedDocument:
    """Complete representation of an ingested document."""

    document_id: str
    """Safe internal identifier (e.g. doc_1a2b3c4d)."""

    filename: str
    """Original sanitized filename."""

    file_type: str
    """'txt' or 'pdf'."""

    pages: list[ExtractedPage] = field(default_factory=list)
    """Page-by-page extracted content."""

    full_text: str = ""
    """Combined text of all pages."""

    total_characters: int = 0
    """Total character count across all pages."""

    is_scanned_or_empty: bool = False
    """True if PDF had pages but zero extractable text (e.g. scanned image)."""

    warnings: list[str] = field(default_factory=list)
    """Informational warnings (e.g. OCR unsupported for scanned PDF)."""


def sanitize_filename(filename: str) -> str:
    """Sanitize filename to prevent directory traversal or unsafe characters."""
    if not filename:
        return "unnamed_document"
    # Extract only the base name (strip directory components)
    clean = Path(filename).name
    # Strip any null bytes or control characters
    clean = re.sub(r"[\x00-\x1f\x7f]", "", clean)
    return clean if clean.strip() else "unnamed_document"


def normalize_document_text(text: str) -> str:
    """Normalize extracted text without destroying sentence boundaries or punctuation.

    - Normalizes CRLF and CR to LF
    - Replaces non-breaking spaces and unusual unicode whitespace with regular space
    - Strips excessive horizontal whitespace per line
    - Collapses 3+ consecutive newlines to 2 newlines (preserving paragraph breaks)
    """
    if not text:
        return ""
    # Normalize newlines
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    # Replace non-breaking spaces and special spaces
    text = re.sub(r"[\u00a0\u1680\u2000-\u200a\u2028\u2029\u202f\u205f\u3000]", " ", text)
    # Collapse multiple horizontal spaces/tabs
    text = re.sub(r"[ \t]+", " ", text)
    # Strip leading/trailing space from lines
    lines = [line.strip() for line in text.split("\n")]
    text = "\n".join(lines)
    # Collapse 3+ newlines to 2
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def ingest_document(
    source: Union[str, Path, bytes, BinaryIO],
    filename: Optional[str] = None,
    max_bytes: Optional[int] = None,
) -> IngestedDocument:
    """Ingest, validate, and extract text from a TXT or PDF document.

    Args:
        source: File path, bytes, or file-like stream.
        filename: Original filename (required if source is bytes or stream).
        max_bytes: Maximum allowed byte size (defaults to configured limit).

    Returns:
        IngestedDocument containing page-level and full text with metadata.

    Raises:
        DocumentValidationError: If file is unsupported, oversized, empty, or corrupt.
    """
    max_allowed = max_bytes if max_bytes is not None else get_max_upload_bytes()

    # Resolve filename and raw bytes
    resolved_filename = ""
    raw_bytes: bytes = b""

    if isinstance(source, (str, Path)):
        path = Path(source)
        if not path.exists():
            raise DocumentValidationError(f"File not found: {path}", code="FILE_NOT_FOUND")
        if not path.is_file():
            raise DocumentValidationError(f"Path is not a regular file: {path}", code="INVALID_FILE")
        resolved_filename = filename or path.name
        file_size = path.stat().st_size
        if file_size > max_allowed:
            raise DocumentValidationError(
                f"File size ({file_size} bytes) exceeds limit of {max_allowed} bytes ({max_allowed // (1024*1024)} MB).",
                code="FILE_TOO_LARGE",
            )
        try:
            raw_bytes = path.read_bytes()
        except OSError as exc:
            raise DocumentValidationError(f"Could not read file: {exc}", code="READ_ERROR") from exc

    elif isinstance(source, bytes):
        if not filename:
            raise DocumentValidationError("Filename must be provided when ingesting bytes.", code="MISSING_FILENAME")
        resolved_filename = filename
        raw_bytes = source

    elif hasattr(source, "read"):
        if not filename:
            resolved_filename = getattr(source, "filename", "") or "unnamed_document"
        else:
            resolved_filename = filename
        try:
            raw_bytes = source.read()
        except Exception as exc:
            raise DocumentValidationError(f"Could not read file stream: {exc}", code="READ_ERROR") from exc
    else:
        raise DocumentValidationError(f"Unsupported source type: {type(source).__name__}", code="INVALID_SOURCE")

    # Check empty bytes
    if len(raw_bytes) == 0:
        raise DocumentValidationError("Uploaded file is empty (0 bytes).", code="EMPTY_FILE")

    # Check size limit
    if len(raw_bytes) > max_allowed:
        raise DocumentValidationError(
            f"File size ({len(raw_bytes)} bytes) exceeds limit of {max_allowed} bytes.",
            code="FILE_TOO_LARGE",
        )

    clean_filename = sanitize_filename(resolved_filename)
    ext = Path(clean_filename).suffix.lower()

    if ext not in [".txt", ".pdf"]:
        raise DocumentValidationError(
            f"Unsupported file extension '{ext}'. Only .txt and .pdf files are supported.",
            code="UNSUPPORTED_FORMAT",
        )

    # Generate safe internal doc ID
    doc_id = f"doc_{uuid.uuid4().hex[:12]}"

    if ext == ".txt":
        return _ingest_txt(raw_bytes, doc_id, clean_filename)
    else:
        return _ingest_pdf(raw_bytes, doc_id, clean_filename)


def _ingest_txt(raw_bytes: bytes, doc_id: str, filename: str) -> IngestedDocument:
    """Ingest and decode plain text."""
    # Attempt UTF-8 first, fallback to Latin-1
    try:
        text = raw_bytes.decode("utf-8")
    except UnicodeDecodeError:
        try:
            text = raw_bytes.decode("latin-1")
        except UnicodeDecodeError as exc:
            raise DocumentValidationError(
                f"Failed to decode text file with UTF-8 or Latin-1: {exc}",
                code="DECODE_ERROR",
            ) from exc

    norm_text = normalize_document_text(text)
    if not norm_text:
        raise DocumentValidationError(
            "Text file contains only whitespace or no readable characters.",
            code="EMPTY_CONTENT",
        )

    page = ExtractedPage(page_number=1, text=norm_text)
    return IngestedDocument(
        document_id=doc_id,
        filename=filename,
        file_type="txt",
        pages=[page],
        full_text=norm_text,
        total_characters=len(norm_text),
        is_scanned_or_empty=False,
        warnings=[],
    )


def _ingest_pdf(raw_bytes: bytes, doc_id: str, filename: str) -> IngestedDocument:
    """Ingest PDF using PyMuPDF (fitz) page-by-page."""
    try:
        import fitz  # PyMuPDF
    except ImportError as exc:
        raise DocumentValidationError(
            "PyMuPDF (fitz) is not installed. PDF ingestion is unavailable.",
            code="DEPENDENCY_MISSING",
        ) from exc

    try:
        doc = fitz.open(stream=raw_bytes, filetype="pdf")
    except Exception as exc:
        raise DocumentValidationError(
            f"Failed to open or parse PDF document: {exc}",
            code="CORRUPT_PDF",
        ) from exc

    try:
        page_count = len(doc)
        if page_count == 0:
            raise DocumentValidationError("PDF document contains 0 pages.", code="EMPTY_PDF")

        pages: list[ExtractedPage] = []
        full_text_parts: list[str] = []
        warnings: list[str] = []

        for page_idx in range(page_count):
            page_obj = doc[page_idx]
            page_text = page_obj.get_text("text") or ""
            norm_page_text = normalize_document_text(page_text)
            page_num = page_idx + 1  # 1-indexed

            pages.append(ExtractedPage(page_number=page_num, text=norm_page_text))
            if norm_page_text:
                full_text_parts.append(norm_page_text)

        full_combined_text = "\n\n".join(full_text_parts).strip()
        is_scanned = len(full_combined_text) == 0

        if is_scanned:
            warnings.append(
                "PDF contains pages but no extractable text. The document appears to be scanned or image-only. "
                "OCR is not supported in this version."
            )

        return IngestedDocument(
            document_id=doc_id,
            filename=filename,
            file_type="pdf",
            pages=pages,
            full_text=full_combined_text,
            total_characters=len(full_combined_text),
            is_scanned_or_empty=is_scanned,
            warnings=warnings,
        )
    finally:
        doc.close()
