"""Inverted index creation for crawled pages."""

from __future__ import annotations

import re
from datetime import datetime, timezone
from typing import Iterable, Protocol


TOKEN_PATTERN = re.compile(r"[A-Za-z0-9]+(?:'[A-Za-z0-9]+)?")


class IndexablePage(Protocol):
    url: str
    title: str
    text: str


def tokenize(text: str) -> list[str]:
    """Return lower-cased searchable tokens from raw text."""

    return [match.group(0).lower() for match in TOKEN_PATTERN.finditer(text)]


def build_inverted_index(pages: Iterable[IndexablePage], source_url: str) -> dict:
    """Build a JSON-serialisable inverted index with frequency and positions."""

    index: dict[str, dict[str, dict[str, object]]] = {}
    page_records: dict[str, dict[str, object]] = {}
    total_terms = 0

    for page in pages:
        tokens = tokenize(page.text)
        page_records[page.url] = {
            "title": page.title,
            "term_count": len(tokens),
            "tokens": tokens,
        }
        total_terms += len(tokens)

        for position, token in enumerate(tokens):
            postings = index.setdefault(token, {})
            page_entry = postings.setdefault(page.url, {"frequency": 0, "positions": []})
            page_entry["frequency"] = int(page_entry["frequency"]) + 1
            page_entry["positions"].append(position)

    return {
        "metadata": {
            "source_url": source_url,
            "built_at": datetime.now(timezone.utc).isoformat(),
            "page_count": len(page_records),
            "total_terms": total_terms,
            "unique_terms": len(index),
        },
        "pages": page_records,
        "index": index,
    }
