"""Search and persistence helpers for the inverted index."""

from __future__ import annotations

import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .indexer import tokenize


DEFAULT_INDEX_PATH = Path("data/index.json")


@dataclass(frozen=True)
class SearchResult:
    url: str
    title: str
    score: float
    term_frequencies: dict[str, int]


class SearchEngine:
    """Load, save, print, and search an inverted index."""

    def __init__(self, index_data: dict[str, Any] | None = None) -> None:
        self.index_data = index_data

    @property
    def loaded(self) -> bool:
        return self.index_data is not None

    def set_index(self, index_data: dict[str, Any]) -> None:
        self.index_data = index_data

    def save(self, path: Path = DEFAULT_INDEX_PATH) -> None:
        self._require_index()
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(self.index_data, indent=2, sort_keys=True), encoding="utf-8")

    def load(self, path: Path = DEFAULT_INDEX_PATH) -> None:
        self.index_data = json.loads(path.read_text(encoding="utf-8"))

    def get_postings(self, word: str) -> dict[str, dict[str, Any]]:
        self._require_index()
        tokens = tokenize(word)
        if not tokens:
            return {}
        return self.index_data["index"].get(tokens[0], {})

    def find(self, query: str) -> list[SearchResult]:
        self._require_index()
        query_terms = list(dict.fromkeys(tokenize(query)))
        if not query_terms:
            return []

        inverted_index = self.index_data["index"]
        posting_sets: list[set[str]] = []
        for term in query_terms:
            postings = inverted_index.get(term)
            if not postings:
                return []
            posting_sets.append(set(postings))

        matching_urls = set.intersection(*posting_sets)
        results: list[SearchResult] = []

        for url in matching_urls:
            term_frequencies = {
                term: int(inverted_index[term][url]["frequency"]) for term in query_terms
            }
            score = self._tf_idf_score(query_terms, url)
            page_info = self.index_data["pages"].get(url, {})
            results.append(
                SearchResult(
                    url=url,
                    title=str(page_info.get("title", url)),
                    score=score,
                    term_frequencies=term_frequencies,
                )
            )

        return sorted(results, key=lambda result: (-result.score, result.url))

    def _tf_idf_score(self, terms: list[str], url: str) -> float:
        """Score a page using term frequency and inverse document frequency."""

        total_pages = max(1, int(self.index_data["metadata"].get("page_count", 0)))
        score = 0.0
        for term in terms:
            postings = self.index_data["index"][term]
            frequency = int(postings[url]["frequency"])
            document_frequency = len(postings)
            inverse_document_frequency = math.log((1 + total_pages) / (1 + document_frequency)) + 1
            score += frequency * inverse_document_frequency
        return round(score, 4)

    def _require_index(self) -> None:
        if self.index_data is None:
            raise RuntimeError("No index is loaded. Run 'build' or 'load' first.")
