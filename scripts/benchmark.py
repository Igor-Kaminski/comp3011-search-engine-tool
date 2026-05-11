"""Simple benchmark for indexing and searching synthetic quote pages."""

from __future__ import annotations

import time
from dataclasses import dataclass
from pathlib import Path
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.indexer import build_inverted_index
from src.search import SearchEngine


@dataclass(frozen=True)
class Page:
    url: str
    title: str
    text: str


def make_pages(page_count: int = 250, repeats: int = 40) -> list[Page]:
    pages: list[Page] = []
    base_text = (
        "good friends share wisdom and stories "
        "indifference fades when friendship and courage survive "
    )
    for number in range(page_count):
        pages.append(
            Page(
                url=f"https://example.test/page/{number}/",
                title=f"Synthetic page {number}",
                text=(base_text + f"unique{number} ") * repeats,
            )
        )
    return pages


def main() -> None:
    pages = make_pages()

    started = time.perf_counter()
    index_data = build_inverted_index(pages, "https://example.test/")
    indexing_seconds = time.perf_counter() - started

    engine = SearchEngine(index_data)
    started = time.perf_counter()
    results = engine.find("good friends")
    search_seconds = time.perf_counter() - started

    print(f"Pages: {index_data['metadata']['page_count']}")
    print(f"Total terms: {index_data['metadata']['total_terms']}")
    print(f"Unique terms: {index_data['metadata']['unique_terms']}")
    print(f"Indexing time: {indexing_seconds:.4f}s")
    print(f"Search time: {search_seconds:.6f}s")
    print(f"Results returned: {len(results)}")


if __name__ == "__main__":
    main()
