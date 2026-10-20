"""Legal glossary loader and lookup for LegalSense.

Loads a curated legal glossary from data/legal_glossary.json and provides
lookup by term. Legal glossary entries are always kept separate from WordNet
synsets and are NOT used in Lesk scoring — they are attached to results as
supplementary domain context.

Design:
- The glossary is a JSON array of objects.
- Each entry must have at least 'term' and 'definition'.
- Optional fields: 'source', 'jurisdiction', 'usage_example', 'limitations'.
- Entries with missing required fields are skipped with a warning.
- The glossary is loaded once and cached in memory.

See docs/WSD_DESIGN.md § 5 for legal-domain safeguards.
"""

from __future__ import annotations

import json
import logging
import os
from pathlib import Path
from typing import Optional

from legalsense.schemas import LegalGlossaryEntry

logger = logging.getLogger(__name__)

# Default glossary path relative to the project root
_DEFAULT_GLOSSARY_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "legal_glossary.json"

# Module-level cache
_glossary: Optional[dict[str, LegalGlossaryEntry]] = None
_loaded_path: Optional[str] = None


class GlossaryLoadError(Exception):
    """Raised when the glossary file cannot be loaded or parsed."""


def load_glossary(
    path: Optional[str | Path] = None,
    *,
    force_reload: bool = False,
) -> dict[str, LegalGlossaryEntry]:
    """Load the legal glossary from a JSON file.

    Args:
        path: Path to the glossary JSON file. Defaults to
              data/legal_glossary.json relative to the project root.
        force_reload: If True, reload even if already cached.

    Returns:
        A dict mapping lowercased term to LegalGlossaryEntry.

    Raises:
        GlossaryLoadError: If the file is missing, unreadable, or has
                           invalid JSON structure.
    """
    global _glossary, _loaded_path

    effective_path = str(path or _DEFAULT_GLOSSARY_PATH)

    if _glossary is not None and not force_reload and _loaded_path == effective_path:
        return _glossary

    if not os.path.isfile(effective_path):
        raise GlossaryLoadError(
            f"Legal glossary file not found: {effective_path}. "
            "Create data/legal_glossary.json or specify a valid path."
        )

    try:
        with open(effective_path, "r", encoding="utf-8") as f:
            raw = json.load(f)
    except json.JSONDecodeError as exc:
        raise GlossaryLoadError(
            f"Invalid JSON in glossary file {effective_path}: {exc}"
        ) from exc
    except OSError as exc:
        raise GlossaryLoadError(
            f"Cannot read glossary file {effective_path}: {exc}"
        ) from exc

    if not isinstance(raw, list):
        raise GlossaryLoadError(
            f"Glossary must be a JSON array, got {type(raw).__name__}."
        )

    glossary: dict[str, LegalGlossaryEntry] = {}
    for i, entry in enumerate(raw):
        if not isinstance(entry, dict):
            logger.warning("Glossary entry %d is not an object; skipped.", i)
            continue

        term = entry.get("term", "").strip()
        definition = entry.get("definition", "").strip()

        if not term or not definition:
            logger.warning(
                "Glossary entry %d missing required 'term' or 'definition'; skipped.",
                i,
            )
            continue

        glossary[term.lower()] = LegalGlossaryEntry(
            term=term,
            definition=definition,
            source=entry.get("source", ""),
            jurisdiction=entry.get("jurisdiction", ""),
            usage_example=entry.get("usage_example", ""),
            limitations=entry.get("limitations", ""),
        )

    _glossary = glossary
    _loaded_path = effective_path
    logger.info("Loaded %d legal glossary entries from %s.", len(glossary), effective_path)
    return glossary


def lookup_term(
    term: str,
    path: Optional[str | Path] = None,
) -> Optional[LegalGlossaryEntry]:
    """Look up a term in the legal glossary.

    Args:
        term: The word or phrase to look up (case-insensitive).
        path: Optional path to the glossary file.

    Returns:
        The matching LegalGlossaryEntry, or None if not found.
    """
    glossary = load_glossary(path)
    return glossary.get(term.lower())


def reset_cache() -> None:
    """Clear the cached glossary. Useful for testing."""
    global _glossary, _loaded_path
    _glossary = None
    _loaded_path = None
