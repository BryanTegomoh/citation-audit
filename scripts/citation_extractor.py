#!/usr/bin/env python3
"""
Citation Extractor Module

Extracts citations from Markdown files (including Quarto .qmd, standard .md,
reStructuredText .rst) in two formats:

  Standard format:  ([Author et al., Year](https://url))
  Title-anchor format: [Paper Title](https://url) (Author et al., Year/preprint)

The title-anchor format is common when the author/year information appears in
parentheses immediately after the hyperlink rather than inside the brackets.
Both formats are extracted and verified through the same pipeline.

Part of the Five-Phase Citation Verification Pipeline.

This tool is domain-agnostic and works with any content containing
markdown-style academic citations.

Supported file types:
- .qmd (Quarto)
- .md (Markdown)
- .rst (reStructuredText with markdown citations)
- .txt (Plain text with markdown citations)
"""

import re
import os
import json
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import List, Optional, Dict, Tuple


@dataclass
class Citation:
    """Represents a single citation extracted from text."""

    # Extracted fields
    citation_text: str  # Full text inside brackets, e.g., "Wong et al., 2021"
    url: str  # Full URL

    # Parsed fields
    authors: str  # Author portion, e.g., "Wong et al."
    year: Optional[str]  # Publication year, e.g., "2021"

    # Context
    file_path: str  # Source file
    line_number: int  # Line where citation appears
    surrounding_text: str  # 200 chars before and after for context

    # Verification status (populated later)
    verified: bool = False
    error_type: Optional[str] = None
    error_details: Optional[str] = None
    corrected_citation: Optional[str] = None

    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)

    @property
    def doi(self) -> Optional[str]:
        """Extract DOI from URL if present."""
        doi_match = re.search(r'10\.\d{4,}/[^\s]+', self.url)
        if doi_match:
            return doi_match.group(0)
        return None

    @property
    def is_doi_url(self) -> bool:
        """Check if URL is a DOI link."""
        return 'doi.org' in self.url.lower()

    @property
    def is_pubmed_url(self) -> bool:
        """Check if URL is a PubMed link."""
        return 'pubmed' in self.url.lower() or 'ncbi.nlm.nih.gov' in self.url.lower()


class CitationExtractor:
    """
    Extracts citations from Markdown/Quarto files.

    Usage:
        extractor = CitationExtractor()
        citations = extractor.extract_from_file("chapter.qmd")
        # or
        citations = extractor.extract_from_directory("./specialties/")
    """

    # Pattern for markdown citations: [text](url)
    # Captures: group(1) = citation text, group(2) = url
    CITATION_PATTERN = re.compile(
        r'\[([^\]]+)\]\((https?://[^\)]+)\)',
        re.IGNORECASE
    )

    # Pattern to identify academic citations vs regular links
    # Academic citations typically have "et al." or "Year" pattern
    ACADEMIC_PATTERN = re.compile(
        r'(?:et\s+al\.?,?\s*)?(?:19|20)\d{2}',
        re.IGNORECASE
    )

    # Pattern to extract author and year from citation text
    AUTHOR_YEAR_PATTERN = re.compile(
        r'^(.+?),?\s*((?:19|20)\d{2})(?:\s*,\s*preprint)?$',
        re.IGNORECASE
    )

    # Pattern for title-as-anchor-text citations where author/year follows the link.
    # Matches: [Paper Title](url) (Author et al., Year) or [Title](url) (Author, preprint)
    # The anchor text must be 15+ chars (distinguishes titles from standard citation text)
    # and must NOT contain a year (otherwise the standard CITATION_PATTERN handles it).
    # Group 1: anchor/title text, Group 2: URL, Group 3: author/year parenthetical
    TITLE_ANCHOR_PATTERN = re.compile(
        r'\[([^\]]{15,})\]\((https?://[^\)]+)\)'   # [Long title](url)
        r'\s*\(([^)]*(?:et\s+al\.?|preprint|(?:19|20)\d{2})[^)]*)\)',  # (Author et al., year/preprint)
        re.IGNORECASE
    )

    # Pattern to check whether anchor text already contains a year
    # (used to avoid double-extracting standard-format citations)
    _YEAR_IN_TEXT = re.compile(r'(?:19|20)\d{2}')

    def __init__(self, context_chars: int = 200):
        """
        Initialize extractor.

        Args:
            context_chars: Number of characters to extract before/after citation
        """
        self.context_chars = context_chars

    def extract_from_file(self, file_path: str) -> List[Citation]:
        """
        Extract all citations from a single file.

        Args:
            file_path: Path to the file to process

        Returns:
            List of Citation objects
        """
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            lines = content.split('\n')

        citations = []
        seen_urls: set = set()

        # Pass 1: standard format — ([Author et al., Year](url))
        for line_num, line in enumerate(lines, start=1):
            for match in self.CITATION_PATTERN.finditer(line):
                citation_text = match.group(1)
                url = match.group(2)

                # Filter to only academic citations
                if not self._is_academic_citation(citation_text):
                    continue

                # Parse author and year
                authors, year = self._parse_author_year(citation_text)

                # Extract surrounding context
                context = self._extract_context(content, match.start(), lines[:line_num])

                citation = Citation(
                    citation_text=citation_text,
                    url=url,
                    authors=authors,
                    year=year,
                    file_path=str(file_path),
                    line_number=line_num,
                    surrounding_text=context
                )

                citations.append(citation)
                seen_urls.add(url.lower().rstrip('/'))

        # Pass 2: title-anchor format — [Paper Title](url) (Author et al., Year/preprint)
        # Catches citations where anchor text is a paper title and author/year follows the link.
        for line_num, line in enumerate(lines, start=1):
            for match in self.TITLE_ANCHOR_PATTERN.finditer(line):
                anchor_text = match.group(1)
                url = match.group(2)
                author_year_text = match.group(3).strip()

                # Skip if anchor text already contains a year (handled by Pass 1)
                if self._YEAR_IN_TEXT.search(anchor_text):
                    continue

                # Skip if already extracted by Pass 1
                if url.lower().rstrip('/') in seen_urls:
                    continue

                # Use the author/year parenthetical as the citation text
                authors, year = self._parse_author_year(author_year_text)

                context = self._extract_context(content, match.start(), lines[:line_num])

                citation = Citation(
                    citation_text=author_year_text,
                    url=url,
                    authors=authors,
                    year=year,
                    file_path=str(file_path),
                    line_number=line_num,
                    surrounding_text=context
                )

                citations.append(citation)
                seen_urls.add(url.lower().rstrip('/'))

        return citations

    def extract_from_directory(
        self,
        directory: str,
        pattern: str = "*.qmd",
        recursive: bool = True
    ) -> List[Citation]:
        """
        Extract citations from all matching files in a directory.

        Args:
            directory: Directory to search
            pattern: Glob pattern for files (default: *.qmd)
            recursive: Whether to search subdirectories

        Returns:
            List of Citation objects from all files
        """
        directory = Path(directory)
        if not directory.exists():
            raise FileNotFoundError(f"Directory not found: {directory}")

        all_citations = []

        if recursive:
            files = directory.rglob(pattern)
        else:
            files = directory.glob(pattern)

        for file_path in files:
            try:
                citations = self.extract_from_file(file_path)
                all_citations.extend(citations)
            except Exception as e:
                print(f"Error processing {file_path}: {e}")

        return all_citations

    def deduplicate(self, citations: List[Citation]) -> Tuple[List[Citation], List[Citation]]:
        """
        Separate unique citations from duplicates.

        Args:
            citations: List of all citations

        Returns:
            Tuple of (unique_citations, duplicate_citations)
        """
        seen_urls = {}
        unique = []
        duplicates = []

        for citation in citations:
            url_key = citation.url.lower().rstrip('/')

            if url_key not in seen_urls:
                seen_urls[url_key] = citation
                unique.append(citation)
            else:
                duplicates.append(citation)

        return unique, duplicates

    def _is_academic_citation(self, text: str) -> bool:
        """Check if citation text looks like an academic reference."""
        return bool(self.ACADEMIC_PATTERN.search(text))

    def _parse_author_year(self, citation_text: str) -> Tuple[str, Optional[str]]:
        """
        Parse author and year from citation text.

        Args:
            citation_text: e.g., "Wong et al., 2021"

        Returns:
            Tuple of (authors, year) or (full_text, None) if parsing fails
        """
        match = self.AUTHOR_YEAR_PATTERN.match(citation_text.strip())
        if match:
            return match.group(1).strip(), match.group(2)
        return citation_text.strip(), None

    def _extract_context(
        self,
        content: str,
        position: int,
        lines_before: List[str]
    ) -> str:
        """Extract surrounding text for context."""
        # Calculate absolute position in content
        abs_pos = sum(len(line) + 1 for line in lines_before[:-1]) + position

        start = max(0, abs_pos - self.context_chars)
        end = min(len(content), abs_pos + self.context_chars)

        return content[start:end].replace('\n', ' ').strip()


def export_citations(citations: List[Citation], output_path: str) -> None:
    """
    Export citations to JSON file.

    Args:
        citations: List of Citation objects
        output_path: Path for output JSON file
    """
    data = {
        'total_count': len(citations),
        'citations': [c.to_dict() for c in citations]
    }

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def main():
    """Command-line interface for the citation extractor."""
    import argparse

    parser = argparse.ArgumentParser(
        description='Extract academic citations from Markdown files',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Extract from a single file
    python citation_extractor.py paper.md -o citations.json

    # Extract from all markdown files in a directory
    python citation_extractor.py ./content/ -o citations.json

    # Extract from Quarto files only
    python citation_extractor.py ./content/ -p "*.qmd" -o citations.json

    # Multiple patterns (use shell expansion)
    python citation_extractor.py ./content/*.md ./content/*.qmd

Supported citation format:
    [Author et al., Year](https://doi.org/...)
    [Author, Year](https://url)
        """
    )
    parser.add_argument('path', help='File or directory path to process')
    parser.add_argument('-o', '--output', default='citations.json', help='Output JSON file')
    parser.add_argument('-p', '--pattern', default='*.md', help='File pattern for directory processing (default: *.md)')
    parser.add_argument('--no-recursive', action='store_true', help='Do not search subdirectories')

    args = parser.parse_args()

    extractor = CitationExtractor()

    path = Path(args.path)
    if path.is_file():
        citations = extractor.extract_from_file(path)
    else:
        citations = extractor.extract_from_directory(
            path,
            pattern=args.pattern,
            recursive=not args.no_recursive
        )

    # Deduplicate
    unique, duplicates = extractor.deduplicate(citations)

    print(f"Total citations found: {len(citations)}")
    print(f"Unique citations: {len(unique)}")
    print(f"Duplicate citations: {len(duplicates)}")

    # Export
    export_citations(unique, args.output)
    print(f"Exported to: {args.output}")


if __name__ == '__main__':
    main()
