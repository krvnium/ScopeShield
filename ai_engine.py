"""Scope auditing with an offline demo mode and optional Gemini integration."""

from __future__ import annotations

import json
import os
from typing import Any

try:
    from dotenv import load_dotenv
except ImportError:  # Keep deterministic offline mode dependency-free.
    def load_dotenv() -> None:
        return None


load_dotenv()

MODEL = "gemma-3-27b-it"
REQUIRED_KEYS = (
    "verdict",
    "requested_feature_summary",
    "page_number",
    "cited_clause",
    "reasoning",
    "estimated_hours",
    "diplomatic_reply",
    "invoice_line_item",
)

RESPONSE_SCHEMA = {
    "type": "OBJECT",
    "properties": {
        "verdict": {"type": "STRING"},
        "requested_feature_summary": {"type": "STRING"},
        "page_number": {"type": "INTEGER"},
        "cited_clause": {"type": "STRING"},
        "reasoning": {"type": "STRING"},
        "estimated_hours": {"type": "NUMBER"},
        "diplomatic_reply": {"type": "STRING"},
        "invoice_line_item": {"type": "STRING"},
    },
    "required": list(REQUIRED_KEYS),
}


def _offline_audit() -> dict[str, Any]:
    return {
        "verdict": "Out of Scope",
        "requested_feature_summary": "Dark Mode & Stripe Payment Gateway",
        "page_number": 2,
        "cited_clause": (
            "Section 3: Exclusions - E-commerce and payment integrations "
            "are not included."
        ),
        "reasoning": (
            "The client requested Stripe integration, which is explicitly "
            "excluded in Section 3."
        ),
        "estimated_hours": 4.5,
        "diplomatic_reply": (
            "Hi! I'd love to add Dark Mode and Stripe for you. Since those "
            "features fall outside our original Statement of Work, it will "
            "take an estimated 4.5 extra hours. Let me know if you'd like "
            "me to log this change order for [TOTAL_COST], and I'll get "
            "right on it!"
        ),
        "invoice_line_item": "Change Order: Dark Mode & Stripe Integration",
    }


def _validate_result(result: Any) -> dict[str, Any]:
    if not isinstance(result, dict) or any(
        key not in result for key in REQUIRED_KEYS
    ):
        raise ValueError("The audit response is missing required fields.")
    return result


def audit_scope(
    pages: list[dict[str, Any]] | str,
    client_message: str,
) -> dict[str, Any]:
    """Audit a client request; use deterministic output when offline."""
    if not client_message.strip():
        raise ValueError("The client message cannot be empty.")

    if not os.getenv("GEMINI_API_KEY"):
        return _offline_audit()

    from google import genai
    from google.genai import types

    if isinstance(pages, str):
        contract = pages
    else:
        contract = "\n\n".join(
            f"[Page {page['page_number']}]\n{page['text']}" for page in pages
        )
    prompt = f"""Audit the client's request against this contract. Return only JSON matching the schema.
Do not provide legal advice. Verdict must be exactly "In Scope" or "Out of Scope".

CONTRACT:
{contract}

CLIENT MESSAGE:
{client_message}"""

    try:
        response = genai.Client(
            api_key=os.environ["GEMINI_API_KEY"]
        ).models.generate_content(
            model=MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=RESPONSE_SCHEMA,
                temperature=0,
            ),
        )
        return _validate_result(json.loads(response.text))
    except json.JSONDecodeError as exc:
        raise ValueError("Gemma returned invalid JSON.") from exc
    except Exception as exc:
        raise RuntimeError(f"Scope audit failed: {exc}") from exc
