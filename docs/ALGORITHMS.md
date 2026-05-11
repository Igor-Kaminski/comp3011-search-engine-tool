# Algorithms and Complexity Notes

This project implements a small search engine pipeline for the quote listing pages on `quotes.toscrape.com`.

## Index Structure

The main data structure is an inverted index:

```text
term -> page URL -> { frequency, positions }
```

Example:

```text
good -> https://quotes.toscrape.com/page/2/ -> frequency=3, positions=[26, 545, 547]
```

The index is paired with a page metadata table:

```text
page URL -> { title, term_count }
```

This structure avoids scanning every page for every search. Instead, search starts from the posting lists for the query terms.

## Crawling

The crawler follows pagination links from the target site's home page. It keeps a `seen` set so the same URL is not crawled twice.

For each successful page:

1. Request the page with a timeout and user agent.
2. Parse HTML with Beautiful Soup.
3. Extract visible text.
4. Locate the next page link using several selector patterns.
5. Wait at least 6 seconds before the next request.

Complexity:

```text
O(P)
```

where `P` is the number of crawled pages, excluding network delay.

## Tokenisation

Text is tokenised with a regular expression and lowercased. This makes search case-insensitive, so `Good`, `GOOD`, and `good` are treated as the same term.

Complexity:

```text
O(T)
```

where `T` is the number of extracted tokens.

## Inverted Index Construction

The indexer scans each token once. For each token it updates:

- The page frequency count.
- The list of positions where the token appears.

Complexity:

```text
O(T)
```

where `T` is the total number of tokens across all pages.

## Multi-Word Search

For a query such as:

```text
find good friends
```

the search engine:

1. Tokenises the query.
2. Gets the posting list for each term.
3. Intersects the sets of page URLs.
4. Scores the matching pages.

Complexity:

```text
O(Q + S)
```

where `Q` is the number of query terms and `S` is the combined size of the posting lists used in the intersection.

## TF-IDF Ranking

The project ranks matching pages with TF-IDF:

```text
score(page, query) = sum(tf(term, page) * idf(term))
```

The IDF calculation is smoothed:

```text
idf(term) = log((1 + total_pages) / (1 + document_frequency)) + 1
```

This means a term that appears on fewer pages contributes more to the score than a very common term.

## Phrase Search

For quoted queries such as:

```text
find "good friends"
```

the search engine uses stored word positions. It checks whether the second term appears exactly one position after the first, the third term appears two positions after the first, and so on.

Complexity:

```text
O(K * M)
```

where `K` is the number of phrase terms and `M` is the number of candidate positions on matching pages.

## Query Suggestions

The suggestion feature uses two strategies:

1. Prefix matching for partial words.
2. Close-match spelling suggestions using Python's `difflib`.

Prefix matching is simple and effective for a small vocabulary. For a much larger index, a trie would be a better data structure for prefix lookup.

## Trade-Offs

- JSON storage is readable and easy to demonstrate, but a larger system would use a database or compressed index.
- The crawler follows quote listing pages rather than every tag and author page. This keeps requests low and makes the crawl deterministic.
- TF-IDF improves ranking while staying explainable, but it does not use semantic similarity or modern neural ranking.

## References

- Christopher D. Manning, Prabhakar Raghavan, and Hinrich Schutze, *Introduction to Information Retrieval*, Cambridge University Press.
- Requests documentation: https://requests.readthedocs.io/
- Beautiful Soup documentation: https://www.crummy.com/software/BeautifulSoup/bs4/doc/
- Python `difflib` documentation: https://docs.python.org/3/library/difflib.html
