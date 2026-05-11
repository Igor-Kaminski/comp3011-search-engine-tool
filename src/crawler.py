"""Crawler for the quotes.toscrape.com coursework target."""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Callable
from urllib.parse import urldefrag, urljoin, urlparse

import requests
from bs4 import BeautifulSoup


DEFAULT_BASE_URL = "https://quotes.toscrape.com/"


@dataclass(frozen=True)
class CrawledPage:
    """A crawled page and the text that will be indexed."""

    url: str
    title: str
    html: str
    text: str


@dataclass(frozen=True)
class CrawlError:
    """A request that failed during crawling."""

    url: str
    message: str


class QuoteCrawler:
    """Crawl quote listing pages while respecting a politeness delay."""

    def __init__(
        self,
        base_url: str = DEFAULT_BASE_URL,
        delay_seconds: float = 6.0,
        timeout_seconds: float = 15.0,
        session: requests.Session | None = None,
        sleep_func: Callable[[float], None] = time.sleep,
        continue_on_error: bool = False,
    ) -> None:
        self.base_url = self._normalise_url(base_url)
        self.delay_seconds = delay_seconds
        self.timeout_seconds = timeout_seconds
        self.session = session or requests.Session()
        self.sleep_func = sleep_func
        self.continue_on_error = continue_on_error
        self.errors: list[CrawlError] = []
        self._request_count = 0
        self._base_domain = urlparse(self.base_url).netloc

    def crawl(self, start_url: str | None = None, max_pages: int | None = None) -> list[CrawledPage]:
        """Crawl the target site's quote pagination until there is no next page."""

        next_url = self._normalise_url(start_url or self.base_url)
        seen: set[str] = set()
        pages: list[CrawledPage] = []

        while next_url and next_url not in seen:
            if max_pages is not None and len(pages) >= max_pages:
                break

            try:
                html = self._fetch(next_url)
            except requests.RequestException as error:
                self.errors.append(CrawlError(next_url, str(error)))
                if not self.continue_on_error:
                    raise
                seen.add(next_url)
                break

            soup = BeautifulSoup(html, "html.parser")
            page = CrawledPage(
                url=next_url,
                title=self._extract_title(soup, next_url),
                html=html,
                text=self._extract_visible_text(soup),
            )
            pages.append(page)
            seen.add(next_url)
            next_url = self._find_next_page_url(soup, next_url)

        return pages

    def _fetch(self, url: str) -> str:
        if self._request_count > 0:
            self.sleep_func(self.delay_seconds)

        try:
            response = self.session.get(
                url,
                headers={"User-Agent": "COMP3011-coursework-search-tool/1.0"},
                timeout=self.timeout_seconds,
            )
        finally:
            self._request_count += 1
        response.raise_for_status()
        return response.text

    def _find_next_page_url(self, soup: BeautifulSoup, current_url: str) -> str | None:
        selectors = (
            "li.next a[href]",
            'a[rel="next"][href]',
            'a[aria-label="Next"][href]',
            "a.next[href]",
        )
        next_link = None
        for selector in selectors:
            next_link = soup.select_one(selector)
            if next_link is not None:
                break

        if next_link is None:
            return None

        next_url = self._normalise_url(urljoin(current_url, next_link["href"]))
        if urlparse(next_url).netloc != self._base_domain:
            return None
        return next_url

    @staticmethod
    def _extract_title(soup: BeautifulSoup, fallback_url: str) -> str:
        if soup.title and soup.title.string:
            return " ".join(soup.title.string.split())
        return fallback_url

    @staticmethod
    def _extract_visible_text(soup: BeautifulSoup) -> str:
        for hidden in soup(["script", "style", "noscript"]):
            hidden.decompose()
        body = soup.body or soup
        return body.get_text(" ", strip=True)

    @staticmethod
    def _normalise_url(url: str) -> str:
        without_fragment, _fragment = urldefrag(url)
        return without_fragment
