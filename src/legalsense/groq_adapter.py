"""Optional Groq LLM contextual assistance adapter for LegalSense.

Provides strictly optional, server-side contextual sense suggestions.
Never exposes API keys or secrets. Operates with timeouts, schema validation,
and graceful fallback to local WSD on any error, rate limit, or missing key.
"""

from __future__ import annotations

import json
import logging
import os
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Optional

from legalsense.schemas import CandidateSense, LegalGlossaryEntry

logger = logging.getLogger(__name__)

# Default Groq model
DEFAULT_GROQ_MODEL = "llama-3.3-70b-versatile"
DEFAULT_TIMEOUT_SECONDS = 6.0


@dataclass
class LLMAssistanceResult:
    """Result of optional LLM contextual assistance."""

    status: str
    """'disabled', 'success', 'unavailable', or 'failed'."""

    suggested_synset_id: Optional[str] = None
    """The candidate synset selected by the LLM, verified against actual candidates."""

    rationale: Optional[str] = None
    """Short explanation from the LLM, if available."""

    warning: Optional[str] = None
    """Warning message if LLM failed, timed out, or hallucinated an invalid synset."""


def is_llm_enabled() -> bool:
    """Check if LLM assistance is configured and enabled."""
    flag = os.getenv("LEGAL_SENSE_ENABLE_LLM", "false").lower()
    if flag in ["0", "false", "no", "off"]:
        return False
    return bool(os.getenv("GROQ_API_KEY"))


def get_configured_model() -> str:
    """Return the configured Groq model name."""
    return os.getenv("GROQ_MODEL", DEFAULT_GROQ_MODEL).strip() or DEFAULT_GROQ_MODEL


def query_groq_wsd_assistance(
    sentence: str,
    target_word: str,
    candidates: list[CandidateSense],
    legal_entry: Optional[LegalGlossaryEntry] = None,
    timeout: float = DEFAULT_TIMEOUT_SECONDS,
) -> LLMAssistanceResult:
    """Query Groq API to obtain an optional contextual interpretation.

    The model is constrained to select only among the provided candidate synset IDs
    or abstain. Hallucinated synset IDs are strictly rejected.

    Args:
        sentence: Sentence context.
        target_word: Word being disambiguated.
        candidates: List of valid WordNet candidate senses.
        legal_entry: Optional legal glossary entry.
        timeout: Network timeout in seconds.

    Returns:
        LLMAssistanceResult with status and validated suggestion.
    """
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        return LLMAssistanceResult(
            status="disabled",
            warning="GROQ_API_KEY is not set. Using local WSD exclusively.",
        )

    flag = os.getenv("LEGAL_SENSE_ENABLE_LLM", "true").lower()
    if flag in ["0", "false", "no", "off"]:
        return LLMAssistanceResult(
            status="disabled",
            warning="LLM assistance is disabled via LEGAL_SENSE_ENABLE_LLM.",
        )

    if not candidates:
        return LLMAssistanceResult(
            status="unavailable",
            warning="No candidate senses available for LLM comparison.",
        )

    valid_synset_ids = {c.synset_id for c in candidates}

    # Build constrained prompt
    candidate_descriptions = "\n".join(
        f"- {c.synset_id} ({c.pos}): {c.definition}" for c in candidates
    )

    legal_info = ""
    if legal_entry:
        legal_info = (
            f"\nNote: A legal glossary definition also exists: '{legal_entry.definition}' "
            f"(Source: {legal_entry.source})."
        )

    system_prompt = (
        "You are a computational linguistics assistant assisting with Word Sense Disambiguation. "
        "Select the single most appropriate WordNet candidate synset ID for the target word in context. "
        "You MUST choose exclusively from the provided candidate synset IDs, or return 'NONE' if no candidate fits. "
        "Respond in strict JSON format with keys 'selected_synset_id' (string) and 'rationale' (concise string)."
    )

    user_prompt = (
        f"Context Sentence: \"{sentence}\"\n"
        f"Target Word: \"{target_word}\"\n\n"
        f"Candidate WordNet Senses:\n{candidate_descriptions}\n"
        f"{legal_info}\n\n"
        "Return JSON only: {\"selected_synset_id\": \"<synset_id or NONE>\", \"rationale\": \"<one sentence>\"}"
    )

    model = get_configured_model()
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": 0.0,
        "max_tokens": 150,
        "response_format": {"type": "json_object"},
    }

    url = "https://api.groq.com/openai/v1/chat/completions"
    data_bytes = json.dumps(payload).encode("utf-8")

    req = urllib.request.Request(
        url,
        data=data_bytes,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "User-Agent": "LegalSense/1.0",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            res_body = response.read().decode("utf-8")
            res_json = json.loads(res_body)

        choices = res_json.get("choices", [])
        if not choices:
            return LLMAssistanceResult(
                status="failed",
                warning="Groq API returned an empty choices array.",
            )

        content_str = choices[0].get("message", {}).get("content", "{}")
        parsed = json.loads(content_str)

        suggested_id = parsed.get("selected_synset_id", "").strip()
        rationale = parsed.get("rationale", "").strip()

        # Strict validation: verify that the suggested_id is actually among the candidate senses
        if suggested_id in valid_synset_ids:
            return LLMAssistanceResult(
                status="success",
                suggested_synset_id=suggested_id,
                rationale=rationale,
            )
        elif suggested_id.upper() == "NONE":
            return LLMAssistanceResult(
                status="success",
                suggested_synset_id=None,
                rationale=rationale or "LLM abstained (no candidate sense fits the legal context).",
            )
        else:
            logger.warning(
                "Groq LLM returned an invalid/hallucinated synset ID '%s' not in candidates. Rejected.",
                suggested_id,
            )
            return LLMAssistanceResult(
                status="failed",
                warning=f"Groq LLM suggested synset ID '{suggested_id}' which is not in candidate senses. Local WSD used.",
            )

    except urllib.error.HTTPError as exc:
        logger.warning("Groq API HTTP error: %s (status %d)", exc.reason, exc.code)
        return LLMAssistanceResult(
            status="failed",
            warning=f"Groq API returned HTTP {exc.code}. Falling back to local WSD.",
        )
    except urllib.error.URLError as exc:
        logger.warning("Groq API connection/timeout error: %s", exc.reason)
        return LLMAssistanceResult(
            status="unavailable",
            warning="Groq API unavailable or timed out. Falling back to local WSD.",
        )
    except Exception as exc:
        logger.warning("Unexpected error during Groq assistance: %s", exc)
        return LLMAssistanceResult(
            status="failed",
            warning=f"Groq assistance error: {exc}. Falling back to local WSD.",
        )
