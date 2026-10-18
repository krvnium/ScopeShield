"""Page-aware PDF parsing and a built-in demo contract."""

from __future__ import annotations

from pathlib import Path
from typing import BinaryIO

import fitz


SAMPLE_CONTRACT = """FREELANCE WEB DEVELOPMENT AGREEMENT

Client: Acme Studio
Contractor: Independent Developer

1. Scope of Work
The Contractor will build a responsive five-page marketing website, including a contact form and deployment to the Client-provided hosting account.

2. Compensation
The fixed project fee is $3,000. Work outside this scope requires a written change order and is billed at $75 per hour.

3. Revisions
Two rounds of revisions to the agreed deliverables are included. New features, pages, or integrations require a change order.
"""


def extract_pages(source: str | Path | bytes | BinaryIO) -> list[dict[str, int | str]]:
    if isinstance(source, (str, Path)):
        document = fitz.open(source)
    elif isinstance(source, bytes):
        document = fitz.open(stream=source, filetype="pdf")
    else:
        document = fitz.open(stream=source.read(), filetype="pdf")
    try:
        return [
            {"page_number": number, "text": page.get_text("text").strip()}
            for number, page in enumerate(document, start=1)
            if page.get_text("text").strip()
        ]
    finally:
        document.close()


def generate_sample_contract() -> bytes:
    document = fitz.open()
    page = document.new_page()
    page.insert_text((72, 72), "FREELANCE WEB DEVELOPMENT AGREEMENT", fontsize=16)
    page.insert_textbox((72, 105, 540, 740), SAMPLE_CONTRACT, fontsize=11, lineheight=1.35)
    data = document.tobytes()
    document.close()
    return data
