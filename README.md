# COMP3011 Search Engine Tool

This project crawls [quotes.toscrape.com](https://quotes.toscrape.com/), builds an inverted index, and lets a user search the saved index from a command-line shell.

The crawler follows the site's quote pagination from the home page to the final page. It waits 6 seconds between successive requests, extracts visible page text with Beautiful Soup, and indexes each lower-case word with its frequency and positions per page.

## Features

- Crawls quote listing pages with a 6-second politeness delay.
- Builds a case-insensitive inverted index with frequency and position statistics.
- Saves and loads the index as JSON.
- Supports single-word, multi-word, and quoted phrase queries.
- Ranks results with TF-IDF scoring.
- Suggests indexed terms for prefixes and likely misspellings.
- Includes unit and integration tests with coverage reporting.
- Runs tests automatically through GitHub Actions.

## Project Structure

```text
src/
  crawler.py
  indexer.py
  search.py
  main.py
tests/
  test_crawler.py
  test_indexer.py
  test_integration.py
  test_main.py
  test_performance.py
  test_search.py
data/
  index.json
docs/
  ALGORITHMS.md
scripts/
  benchmark.py
.github/workflows/
  tests.yml
requirements.txt
README.md
```

## Setup

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

You can also install the requirements into your current Python environment:

```powershell
python -m pip install -r requirements.txt
```

## Usage

Start the shell:

```powershell
python -m src.main
```

Build and save the index:

```text
> build
```

Load a previously saved index:

```text
> load
```

Print the inverted index for a word:

```text
> print nonsense
```

Find pages containing all query words:

```text
> find indifference
> find good friends
```

Find an exact phrase by wrapping it in double quotes:

```text
> find "good friends"
```

Ask for suggestions when you have a partial word or likely misspelling:

```text
> suggest friend
> suggest indiference
```

Helpful edge cases to demonstrate:

```text
> find
> print qwertywordnotfound
> find qwertywordnotfound
```

## Testing

Run the tests:

```powershell
python -m pytest
```

Run tests with coverage:

```powershell
python -m pytest --cov=src --cov-report=term-missing
```

The crawler tests use fake pages and a fake sleep function, so they do not contact the website or wait 6 seconds during testing.

Run the synthetic benchmark:

```powershell
python scripts/benchmark.py
```

The benchmark builds an index over generated pages and times indexing plus search. It is intended as lightweight evidence for algorithmic performance, not as a replacement for unit tests.

## Design Notes

The implementation is split into small modules so each responsibility is isolated and testable:

- `crawler.py`: HTTP requests, HTML parsing, pagination, request delay, and request error handling.
- `indexer.py`: tokenisation and inverted index construction.
- `search.py`: JSON persistence, posting-list lookup, TF-IDF ranking, phrase search, and suggestions.
- `main.py`: command-line shell and user-facing command output.

This separation keeps the crawler independent from the search algorithm. It also allows tests to mock network requests without touching the indexer or CLI.

## Data Structures and Algorithms

More detail is available in `docs/ALGORITHMS.md`.

The inverted index is stored as JSON in `data/index.json`. Each term maps to the pages where it appears, and each page entry stores:

- `frequency`: how many times the word appears on that page.
- `positions`: zero-based word positions in the extracted page text.

Conceptually, the main structure is:

```text
term -> page URL -> { frequency, positions }
```

The supporting `pages` dictionary stores page-level metadata:

```text
page URL -> { title, term_count }
```

The main algorithms are:

- **Tokenisation**: a regular expression extracts word-like tokens and lowercases them, making search case-insensitive.
- **Inverted indexing**: one pass over each page's tokens builds posting lists with frequencies and positions.
- **Boolean AND search**: multi-word search intersects the posting lists for each query term, returning only pages that contain all query words.
- **TF-IDF ranking**: matching pages are scored by combining term frequency with inverse document frequency, so rarer terms have more influence.
- **Phrase search**: quoted queries use the stored word positions to check whether terms occur next to each other in order.
- **Suggestions**: prefix matching is tried first, followed by close-match spelling suggestions using Python's standard library.

These structures are efficient for the coursework-sized site because dictionary lookups are fast and posting-list intersections avoid scanning every page during search.

## Error Handling and Defensive Behaviour

The crawler uses timeouts and `raise_for_status()` so failed HTTP responses are detected. In normal command-line builds it uses graceful mode: if a request fails, the error is recorded and the build avoids crashing the shell. If no pages can be crawled, the user receives a clear build failure message instead of an empty index.

The CLI also handles common user mistakes:

- Missing saved index file.
- Searching before loading or building an index.
- Empty `print`, `find`, or `suggest` commands.
- Words or queries that do not exist in the index.

Crawler tests use fake sessions and fake responses to verify these behaviours without depending on the live website.

## Design Rationale

The crawler intentionally follows the quote listing pagination instead of crawling every tag and author link. This keeps the crawl deterministic, avoids unnecessary requests, and matches the examples in the coursework brief. The trade-off is that author biography pages are not indexed.

JSON was chosen for the saved index because it is human-readable, easy to inspect during the video demonstration, and sufficient for this dataset size. A larger search engine would usually use a database or a compressed index format.

TF-IDF was added as an advanced feature because it improves ranking quality while still being explainable from the existing index statistics. Phrase search reuses the stored positions, which demonstrates why the index records more than simple word presence.

## GenAI Use Declaration

This implementation was developed with help from OpenAI Codex. The AI was used to interpret the coursework brief, scaffold the project structure, implement the crawler/index/search modules, write tests, and draft documentation. You should declare this in the video demonstration and be ready to explain the design decisions and code in your own words.

## Continuous Integration

The repository includes a GitHub Actions workflow in `.github/workflows/tests.yml`. It installs the dependencies and runs:

```powershell
python -m pytest --cov=src --cov-report=term-missing
```

This gives automated test feedback whenever commits are pushed to GitHub.
