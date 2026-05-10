from __future__ import annotations

import requests
import pytest

from src.crawler import QuoteCrawler


class FakeResponse:
    def __init__(self, text: str, status_code: int = 200) -> None:
        self.text = text
        self.status_code = status_code

    def raise_for_status(self) -> None:
        if self.status_code >= 400:
            raise requests.HTTPError(f"{self.status_code} error")


class FakeSession:
    def __init__(self, pages: dict[str, FakeResponse]) -> None:
        self.pages = pages
        self.requested_urls: list[str] = []

    def get(self, url: str, headers: dict[str, str], timeout: float) -> FakeResponse:
        self.requested_urls.append(url)
        return self.pages[url]


def test_crawler_follows_next_links_and_respects_politeness_delay() -> None:
    base_url = "https://quotes.toscrape.com/"
    second_url = "https://quotes.toscrape.com/page/2/"
    session = FakeSession(
        {
            base_url: FakeResponse(
                """
                <html>
                  <head><title>Quotes page 1</title></head>
                  <body>
                    <span class="text">Good friends matter.</span>
                    <li class="next"><a href="/page/2/">Next</a></li>
                  </body>
                </html>
                """
            ),
            second_url: FakeResponse(
                """
                <html>
                  <head><title>Quotes page 2</title></head>
                  <body><span class="text">Indifference is not wisdom.</span></body>
                </html>
                """
            ),
        }
    )
    sleep_calls: list[float] = []

    crawler = QuoteCrawler(base_url=base_url, session=session, sleep_func=sleep_calls.append)
    pages = crawler.crawl()

    assert [page.url for page in pages] == [base_url, second_url]
    assert [page.title for page in pages] == ["Quotes page 1", "Quotes page 2"]
    assert "Good friends matter." in pages[0].text
    assert session.requested_urls == [base_url, second_url]
    assert sleep_calls == [6.0]


def test_crawler_stops_at_max_pages() -> None:
    base_url = "https://quotes.toscrape.com/"
    second_url = "https://quotes.toscrape.com/page/2/"
    session = FakeSession(
        {
            base_url: FakeResponse('<html><body><li class="next"><a href="/page/2/">Next</a></li></body></html>'),
            second_url: FakeResponse("<html><body>Second page</body></html>"),
        }
    )

    crawler = QuoteCrawler(base_url=base_url, session=session, sleep_func=lambda seconds: None)
    pages = crawler.crawl(max_pages=1)

    assert len(pages) == 1
    assert session.requested_urls == [base_url]


def test_crawler_raises_for_http_errors() -> None:
    base_url = "https://quotes.toscrape.com/"
    crawler = QuoteCrawler(
        base_url=base_url,
        session=FakeSession({base_url: FakeResponse("Missing", status_code=404)}),
        sleep_func=lambda seconds: None,
    )

    with pytest.raises(requests.HTTPError):
        crawler.crawl()
