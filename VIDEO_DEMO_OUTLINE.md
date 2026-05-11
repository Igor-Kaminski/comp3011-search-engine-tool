# 5-Minute Video Demonstration Outline

Use this as a timing guide. Keep the narration natural and only say things you understand and can justify.

## 0:00-2:00 Live Demonstration

Show the terminal from the repository root.

```powershell
python -m src.main
```

Commands to demonstrate:

```text
> build
> load
> print nonsense
> find indifference
> find good friends
> find "good friends"
> suggest indiference
> find
> print qwertywordnotfound
> find qwertywordnotfound
```

Mention that `build` crawls 10 quote listing pages and waits 6 seconds between successive requests.

## 2:00-3:30 Code Walkthrough and Design Decisions

- `src/crawler.py`: follows the site's pagination, extracts visible text with Beautiful Soup, and enforces the politeness delay.
- `src/indexer.py`: tokenises text case-insensitively and builds an inverted index.
- `src/search.py`: stores and loads JSON, prints postings, and finds pages containing all query terms.
- Advanced search: TF-IDF scoring ranks results, quoted queries use word positions for exact phrase search, and `suggest` offers prefix/spelling suggestions.
- `src/main.py`: provides the interactive shell commands required by the brief.

Data structure to explain:

```text
word -> page URL -> frequency and positions
```

Example:

```text
good -> https://quotes.toscrape.com/ -> frequency=1, positions=[...]
```

Trade-off to mention: the crawler follows quote pagination rather than every author/tag link so the crawl is deterministic and focused on the quote pages used by the assignment examples.

Algorithms to mention:

- Posting-list intersection for multi-word search.
- TF-IDF ranking for result ordering.
- Position checks for exact phrase search.
- Prefix and close-match lookup for suggestions.
- Graceful crawler error handling with request timeouts and recorded errors.

## 3:30-4:00 Testing

Run:

```powershell
python -m pytest --cov=src --cov-report=term-missing
```

Optionally show the benchmark:

```powershell
python scripts/benchmark.py
```

Mention:

- Crawler tests use fake HTTP pages and fake sleep calls.
- Indexer tests check case-insensitive tokenisation, frequencies, and positions.
- Search tests check TF-IDF ranking, phrase queries, suggestions, missing words, save/load, and unloaded-index errors.
- Integration tests check the full index-save-load-search workflow.
- Performance tests and `scripts/benchmark.py` provide lightweight evidence for indexing/search efficiency.
- Current result: run the command above and quote the test/coverage result shown on your machine.
- The GitHub Actions workflow runs the same pytest command automatically after pushing to GitHub.

## 4:00-4:30 Version Control

Run:

```powershell
git log --oneline --decorate --max-count=10
```

Mention the development sequence:

- Core crawler/index/search modules.
- Ignore generated Python cache files.
- CLI and README.
- Tests.
- Generated index file.

## 4:30-5:00 GenAI Critical Evaluation

Suggested points to adapt into your own words:

- Codex helped interpret the brief, create the project structure, implement the first version, and write tests.
- The AI-assisted workflow still needed verification: `compileall` accidentally produced `__pycache__` files that were committed at first, then fixed with `.gitignore` and a cleanup commit.
- The tests were especially useful because they check the crawler logic without making slow real website requests.
- You learned that the inverted index maps each word to page-level statistics, and that multi-word search can be implemented by intersecting the posting lists for each query term.
- You should declare Codex/OpenAI use clearly because the brief says non-declared GenAI use is academic misconduct.
