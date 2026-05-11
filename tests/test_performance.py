from __future__ import annotations

import time
from dataclasses import dataclass

from src.indexer import build_inverted_index
from src.search import SearchEngine


@dataclass(frozen=True)
class Page:
    url: str
    title: str
    text: str


def test_index_and_search_complete_quickly_on_synthetic_dataset() -> None:
    pages = [
        Page(
            f"https://example.test/{number}",
            f"Page {number}",
            ("good friends wisdom friendship indifference " * 30) + f"unique{number}",
        )
        for number in range(100)
    ]

    started = time.perf_counter()
    index_data = build_inverted_index(pages, "https://example.test/")
    engine = SearchEngine(index_data)
    results = engine.find("good friends")
    elapsed = time.perf_counter() - started

    assert len(results) == 100
    assert index_data["metadata"]["total_terms"] == 15100
    assert elapsed < 1.0
