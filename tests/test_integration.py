from __future__ import annotations

from dataclasses import dataclass

from src.indexer import build_inverted_index
from src.search import SearchEngine


@dataclass(frozen=True)
class Page:
    url: str
    title: str
    text: str


def test_index_search_and_suggestion_workflow(tmp_path) -> None:
    pages = [
        Page("https://example.test/1", "One", "Good friends tell good stories"),
        Page("https://example.test/2", "Two", "Friendship survives indifference"),
        Page("https://example.test/3", "Three", "Good ideas survive"),
    ]
    index_data = build_inverted_index(pages, "https://example.test/")
    path = tmp_path / "index.json"

    built_engine = SearchEngine(index_data)
    built_engine.save(path)

    loaded_engine = SearchEngine()
    loaded_engine.load(path)

    results = loaded_engine.find("good")
    assert [result.url for result in results] == [
        "https://example.test/1",
        "https://example.test/3",
    ]
    assert loaded_engine.find('"good friends"')[0].url == "https://example.test/1"
    assert loaded_engine.find('"friends good"') == []
    assert loaded_engine.suggest("indiference") == ["indifference"]


def test_phrase_search_requires_adjacent_positions() -> None:
    pages = [
        Page("https://example.test/1", "One", "good wise friends"),
        Page("https://example.test/2", "Two", "good friends"),
    ]
    engine = SearchEngine(build_inverted_index(pages, "https://example.test/"))

    results = engine.find('"good friends"')

    assert [result.url for result in results] == ["https://example.test/2"]
