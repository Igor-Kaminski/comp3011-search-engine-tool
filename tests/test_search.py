from __future__ import annotations

import pytest

from src.search import SearchEngine


def sample_index() -> dict:
    return {
        "metadata": {
            "source_url": "https://quotes.toscrape.com/",
            "built_at": "2026-05-11T00:00:00+00:00",
            "page_count": 2,
            "total_terms": 8,
            "unique_terms": 5,
        },
        "pages": {
            "https://quotes.toscrape.com/": {
                "title": "Home",
                "term_count": 5,
                "tokens": ["good", "ideas", "matter", "good", "friends"],
            },
            "https://quotes.toscrape.com/page/2/": {
                "title": "Page 2",
                "term_count": 3,
                "tokens": ["indifference", "good", "friendship"],
            },
        },
        "index": {
            "good": {
                "https://quotes.toscrape.com/": {"frequency": 2, "positions": [0, 3]},
                "https://quotes.toscrape.com/page/2/": {"frequency": 1, "positions": [1]},
            },
            "friends": {
                "https://quotes.toscrape.com/": {"frequency": 1, "positions": [4]},
            },
            "indifference": {
                "https://quotes.toscrape.com/page/2/": {"frequency": 1, "positions": [0]},
            },
            "friendship": {
                "https://quotes.toscrape.com/page/2/": {"frequency": 1, "positions": [2]},
            },
        },
    }


def test_find_returns_pages_containing_all_query_terms_ranked_by_tfidf_score() -> None:
    engine = SearchEngine(sample_index())

    results = engine.find("good friends")

    assert len(results) == 1
    assert results[0].url == "https://quotes.toscrape.com/"
    assert results[0].score == 3.4055
    assert results[0].term_frequencies == {"good": 2, "friends": 1}
    assert results[0].snippet == "good ideas matter good friends"


def test_tfidf_ranking_rewards_rarer_terms() -> None:
    engine = SearchEngine(sample_index())

    results = engine.find("good")

    assert [result.url for result in results] == [
        "https://quotes.toscrape.com/",
        "https://quotes.toscrape.com/page/2/",
    ]
    assert results[0].score > results[1].score


def test_find_returns_empty_for_missing_or_empty_queries() -> None:
    engine = SearchEngine(sample_index())

    assert engine.find("doesnotexist") == []
    assert engine.find("   ") == []


def test_find_supports_exact_quoted_phrase_queries() -> None:
    engine = SearchEngine(sample_index())

    assert [result.url for result in engine.find('"good friends"')] == [
        "https://quotes.toscrape.com/"
    ]
    assert engine.find('"friends good"') == []


def test_suggest_returns_prefix_and_close_matches() -> None:
    engine = SearchEngine(sample_index())

    assert engine.suggest("friend") == ["friends", "friendship"]
    assert engine.suggest("indiference") == ["indifference"]
    assert engine.suggest("   ") == []


def test_get_postings_uses_first_valid_word() -> None:
    engine = SearchEngine(sample_index())

    postings = engine.get_postings("Good!")

    assert set(postings) == {
        "https://quotes.toscrape.com/",
        "https://quotes.toscrape.com/page/2/",
    }


def test_save_and_load_round_trip(tmp_path) -> None:
    path = tmp_path / "index.json"
    original = SearchEngine(sample_index())
    original.save(path)

    loaded = SearchEngine()
    loaded.load(path)

    assert loaded.index_data == sample_index()


def test_stats_summarises_loaded_index() -> None:
    engine = SearchEngine(sample_index())

    stats = engine.stats()

    assert stats["page_count"] == 2
    assert stats["unique_terms"] == 5
    assert stats["largest_page_terms"] == 5
    assert stats["most_common_terms"][0] == ("good", 3)


def test_validate_reports_structural_errors() -> None:
    bad_index = sample_index()
    bad_index["index"]["good"]["https://quotes.toscrape.com/"]["frequency"] = 99

    errors = SearchEngine.validate(bad_index)

    assert errors == ["frequency mismatch for 'good' on 'https://quotes.toscrape.com/'"]


def test_search_requires_loaded_index() -> None:
    engine = SearchEngine()

    with pytest.raises(RuntimeError, match="No index is loaded"):
        engine.find("good")
