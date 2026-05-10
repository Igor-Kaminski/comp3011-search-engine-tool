from __future__ import annotations

from dataclasses import dataclass

from src.indexer import build_inverted_index, tokenize


@dataclass(frozen=True)
class Page:
    url: str
    title: str
    text: str


def test_tokenize_is_case_insensitive_and_ignores_punctuation() -> None:
    assert tokenize("Good, GOOD! friends.") == ["good", "good", "friends"]


def test_build_inverted_index_stores_frequency_and_positions() -> None:
    pages = [
        Page("https://example.test/1", "One", "Good good friends"),
        Page("https://example.test/2", "Two", "Nonsense and good"),
    ]

    index_data = build_inverted_index(pages, "https://example.test/")

    assert index_data["metadata"]["page_count"] == 2
    assert index_data["metadata"]["total_terms"] == 6
    assert index_data["metadata"]["unique_terms"] == 4
    assert index_data["pages"]["https://example.test/1"]["term_count"] == 3
    assert index_data["index"]["good"]["https://example.test/1"] == {
        "frequency": 2,
        "positions": [0, 1],
    }
    assert index_data["index"]["good"]["https://example.test/2"] == {
        "frequency": 1,
        "positions": [2],
    }
