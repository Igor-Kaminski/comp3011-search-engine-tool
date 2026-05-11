from __future__ import annotations

from dataclasses import dataclass

import pytest

from src.main import SearchShell
from src.search import SearchEngine


@dataclass(frozen=True)
class Page:
    url: str
    title: str
    text: str


def test_shell_handles_help_unknown_empty_and_exit() -> None:
    shell = SearchShell()

    assert "Available commands" in shell.execute("")
    assert "Commands:" in shell.execute("help")
    assert "Unknown command" in shell.execute("dance")
    with pytest.raises(EOFError):
        shell.execute("exit")


def test_shell_reports_missing_index_before_print_or_find() -> None:
    shell = SearchShell()

    assert "No index is loaded" in shell.execute("print good")
    assert "No index is loaded" in shell.execute("find good")
    assert "Usage: print <word>" == shell.execute("print")
    assert "Usage: find <word> [more words]" == shell.execute("find")


def test_shell_load_print_and_find(tmp_path) -> None:
    index_path = tmp_path / "index.json"
    engine = SearchEngine(
        {
            "metadata": {
                "source_url": "https://quotes.toscrape.com/",
                "built_at": "2026-05-11T00:00:00+00:00",
                "page_count": 1,
                "total_terms": 3,
                "unique_terms": 2,
            },
            "pages": {
                "https://quotes.toscrape.com/": {"title": "Home", "term_count": 3},
            },
            "index": {
                "good": {
                    "https://quotes.toscrape.com/": {"frequency": 2, "positions": [0, 2]},
                },
                "friends": {
                    "https://quotes.toscrape.com/": {"frequency": 1, "positions": [1]},
                },
                "friendship": {
                    "https://quotes.toscrape.com/": {"frequency": 1, "positions": [2]},
                },
            },
        }
    )
    engine.save(index_path)

    shell = SearchShell(index_path=index_path)

    assert "Loaded index" in shell.execute("load")
    assert "frequency=2" in shell.execute("print good")
    assert "No entries found" in shell.execute("print missing")
    assert "Found 1 page(s)" in shell.execute("find good friends")
    assert "Found 1 page(s)" in shell.execute('find "good friends"')
    assert "Suggestions for 'friend'" in shell.execute("suggest friend")
    assert "No pages found" in shell.execute("find missing")


def test_shell_reports_missing_saved_index(tmp_path) -> None:
    shell = SearchShell(index_path=tmp_path / "missing.json")

    assert "Run 'build' first" in shell.execute("load")


def test_shell_build_crawls_indexes_and_saves(tmp_path, monkeypatch) -> None:
    class FakeCrawler:
        errors = []

        def __init__(self, base_url: str, delay_seconds: float, continue_on_error: bool) -> None:
            assert base_url == "https://example.test/"
            assert delay_seconds == 0
            assert continue_on_error is True

        def crawl(self) -> list[Page]:
            return [Page("https://example.test/", "Example", "Alpha beta alpha")]

    monkeypatch.setattr("src.main.QuoteCrawler", FakeCrawler)
    index_path = tmp_path / "index.json"
    shell = SearchShell(index_path=index_path, base_url="https://example.test/", delay_seconds=0)

    output = shell.execute("build")

    assert "Built index for 1 pages" in output
    assert index_path.exists()
    loaded = SearchEngine()
    loaded.load(index_path)
    assert loaded.get_postings("alpha")["https://example.test/"]["frequency"] == 2
