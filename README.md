# COMP3011 Search Engine Tool

This project crawls [quotes.toscrape.com](https://quotes.toscrape.com/), builds an inverted index, and lets a user search the saved index from a command-line shell.

The crawler follows the site's quote pagination from the home page to the final page. It waits 6 seconds between successive requests, extracts visible page text with Beautiful Soup, and indexes each lower-case word with its frequency and positions per page.

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
  test_search.py
data/
  index.json
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

## Design Notes

- `crawler.py` is responsible for HTTP requests, HTML parsing, pagination, and the 6-second politeness window.
- `indexer.py` tokenises page text and builds the inverted index.
- `search.py` saves, loads, prints postings, and searches for pages that contain all query terms.
- `main.py` provides the interactive command-line shell required by the brief.

The inverted index is stored as JSON in `data/index.json`. Each term maps to the pages where it appears, and each page entry stores:

- `frequency`: how many times the word appears on that page.
- `positions`: zero-based word positions in the extracted page text.

## GenAI Use Declaration

This implementation was developed with help from OpenAI Codex. The AI was used to interpret the coursework brief, scaffold the project structure, implement the crawler/index/search modules, write tests, and draft documentation. You should declare this in the video demonstration and be ready to explain the design decisions and code in your own words.
