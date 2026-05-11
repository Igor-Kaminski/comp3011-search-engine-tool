"""Command-line shell for the search tool."""

from __future__ import annotations

import argparse
from pathlib import Path

from .crawler import DEFAULT_BASE_URL, QuoteCrawler
from .indexer import build_inverted_index, tokenize
from .search import DEFAULT_INDEX_PATH, SearchEngine


class SearchShell:
    """Small command shell implementing build, load, print, and find."""

    def __init__(
        self,
        index_path: Path = DEFAULT_INDEX_PATH,
        base_url: str = DEFAULT_BASE_URL,
        delay_seconds: float = 6.0,
    ) -> None:
        self.index_path = index_path
        self.base_url = base_url
        self.delay_seconds = delay_seconds
        self.engine = SearchEngine()

    def execute(self, line: str) -> str:
        command, argument = self._split_command(line)

        if command == "":
            return "Please enter a command. Available commands: build, load, print, find, help, exit."
        if command == "build":
            return self._build()
        if command == "load":
            return self._load()
        if command == "print":
            return self._print(argument)
        if command == "find":
            return self._find(argument)
        if command == "suggest":
            return self._suggest(argument)
        if command == "help":
            return self._help()
        if command in {"exit", "quit"}:
            raise EOFError
        return f"Unknown command '{command}'. Type 'help' for available commands."

    def _build(self) -> str:
        crawler = QuoteCrawler(base_url=self.base_url, delay_seconds=self.delay_seconds)
        pages = crawler.crawl()
        index_data = build_inverted_index(pages, self.base_url)
        self.engine.set_index(index_data)
        self.engine.save(self.index_path)
        metadata = index_data["metadata"]
        return (
            f"Built index for {metadata['page_count']} pages, "
            f"{metadata['unique_terms']} unique terms, "
            f"{metadata['total_terms']} total terms. Saved to {self.index_path}."
        )

    def _load(self) -> str:
        try:
            self.engine.load(self.index_path)
        except FileNotFoundError:
            return f"No saved index found at {self.index_path}. Run 'build' first."

        metadata = self.engine.index_data["metadata"]
        return (
            f"Loaded index from {self.index_path}: "
            f"{metadata['page_count']} pages and {metadata['unique_terms']} unique terms."
        )

    def _print(self, argument: str) -> str:
        tokens = tokenize(argument)
        if not tokens:
            return "Usage: print <word>"

        word = tokens[0]
        try:
            postings = self.engine.get_postings(word)
        except RuntimeError as error:
            return str(error)

        if not postings:
            return f"No entries found for '{word}'."

        lines = [f"Inverted index for '{word}' ({len(postings)} page(s)):"]
        sorted_postings = sorted(
            postings.items(),
            key=lambda item: (-int(item[1]["frequency"]), item[0]),
        )
        for url, entry in sorted_postings:
            positions = entry["positions"]
            preview = ", ".join(str(position) for position in positions[:20])
            if len(positions) > 20:
                preview += ", ..."
            lines.append(f"- {url} | frequency={entry['frequency']} | positions=[{preview}]")
        return "\n".join(lines)

    def _find(self, argument: str) -> str:
        if not tokenize(argument):
            return "Usage: find <word> [more words]"

        try:
            results = self.engine.find(argument)
        except RuntimeError as error:
            return str(error)

        if not results:
            suggestions = self.engine.suggest(argument)
            if suggestions:
                return (
                    f"No pages found for '{argument.strip()}'. "
                    f"Suggestions: {', '.join(suggestions)}."
                )
            return f"No pages found for '{argument.strip()}'."

        lines = [f"Found {len(results)} page(s) for '{argument.strip()}':"]
        for result in results:
            frequencies = ", ".join(
                f"{term}={frequency}" for term, frequency in result.term_frequencies.items()
            )
            lines.append(f"- {result.url} | tf-idf={result.score:.4f} | {frequencies}")
        return "\n".join(lines)

    def _suggest(self, argument: str) -> str:
        if not tokenize(argument):
            return "Usage: suggest <word>"

        try:
            suggestions = self.engine.suggest(argument)
        except RuntimeError as error:
            return str(error)

        if not suggestions:
            return f"No suggestions found for '{argument.strip()}'."
        return f"Suggestions for '{argument.strip()}': {', '.join(suggestions)}"

    @staticmethod
    def _split_command(line: str) -> tuple[str, str]:
        stripped = line.strip()
        if not stripped:
            return "", ""
        command, _, argument = stripped.partition(" ")
        return command.lower(), argument.strip()

    @staticmethod
    def _help() -> str:
        return "\n".join(
            [
                "Commands:",
                "  build              Crawl the website, build the index, and save it.",
                "  load               Load the saved index from disk.",
                "  print <word>       Print postings for one word.",
                "  find <query>       Find pages containing all query words.",
                '  find "<phrase>"    Find pages containing an exact phrase.',
                "  suggest <word>     Suggest indexed terms for a prefix or misspelling.",
                "  exit               Close the shell.",
            ]
        )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="COMP3011 quote search tool")
    parser.add_argument("--index", default=str(DEFAULT_INDEX_PATH), help="Path to index JSON file")
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL, help="Website URL to crawl")
    parser.add_argument(
        "--delay",
        type=float,
        default=6.0,
        help="Politeness delay in seconds between successive requests",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    shell = SearchShell(
        index_path=Path(args.index),
        base_url=args.base_url,
        delay_seconds=args.delay,
    )
    print("COMP3011 Search Tool. Type 'help' for commands.")

    while True:
        try:
            line = input("> ")
            output = shell.execute(line)
            print(output)
        except EOFError:
            print("Goodbye.")
            break
        except KeyboardInterrupt:
            print("\nGoodbye.")
            break


if __name__ == "__main__":
    main()
