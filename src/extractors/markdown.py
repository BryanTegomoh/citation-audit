"""Extract citations from Markdown files."""

import re
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional


@dataclass
class Citation:
    """Represents an extracted citation."""

    doi: str
    text: str  # The citation text (e.g., "Smith et al., 2020")
    context: str  # Surrounding text for context
    line_number: int
    file_path: str

    # Extracted metadata from citation text (may be None)
    claimed_author: Optional[str] = None
    claimed_year: Optional[int] = None
    claimed_journal: Optional[str] = None


# Regex patterns for DOI extraction
DOI_PATTERNS = [
    # Markdown link with DOI URL: [text](https://doi.org/10.xxxx/yyyy)
    r'\[([^\]]+)\]\(https?://(?:dx\.)?doi\.org/(10\.\d{4,}/[^\s\)]+)\)',

    # Markdown link with direct DOI: [text](doi:10.xxxx/yyyy)
    r'\[([^\]]+)\]\(doi:(10\.\d{4,}/[^\s\)]+)\)',

    # Plain DOI URL: https://doi.org/10.xxxx/yyyy
    r'https?://(?:dx\.)?doi\.org/(10\.\d{4,}/[^\s\)>\]]+)',

    # DOI with prefix: doi:10.xxxx/yyyy or DOI: 10.xxxx/yyyy
    r'(?:doi:|DOI:)\s*(10\.\d{4,}/[^\s\)>\]]+)',

    # Raw DOI (less reliable, use as fallback)
    r'\b(10\.\d{4,}/[^\s\)>\]]+)\b',
]

# Pattern to extract author and year from citation text
AUTHOR_YEAR_PATTERN = re.compile(
    r'(?P<author>[A-Z][a-z]+(?:\s+(?:et\s+al\.?|and\s+[A-Z][a-z]+))?)'
    r'[,\s]+(?:\(?(?P<year>(?:19|20)\d{2})\)?)',
    re.IGNORECASE
)


def extract_author_year(text: str) -> tuple[Optional[str], Optional[int]]:
    """Extract author name and year from citation text.

    Args:
        text: Citation text like "Smith et al., 2020" or "Smith and Jones (2019)"

    Returns:
        Tuple of (author_name, year) or (None, None) if not found
    """
    match = AUTHOR_YEAR_PATTERN.search(text)
    if match:
        author = match.group('author')
        year_str = match.group('year')
        year = int(year_str) if year_str else None
        return author, year
    return None, None


def clean_doi(doi: str) -> str:
    """Clean and normalize a DOI string.

    Args:
        doi: Raw DOI string

    Returns:
        Cleaned DOI string
    """
    # Remove trailing punctuation that might have been captured
    doi = doi.rstrip('.,;:')

    # Remove any URL encoding artifacts
    doi = doi.replace('%2F', '/')

    # Remove trailing parentheses if unbalanced
    if doi.endswith(')') and doi.count('(') < doi.count(')'):
        doi = doi.rstrip(')')

    return doi


def get_context(lines: List[str], line_idx: int, context_chars: int = 100) -> str:
    """Get surrounding context for a citation.

    Args:
        lines: All lines of the file
        line_idx: Index of the line containing the citation
        context_chars: Approximate number of characters of context

    Returns:
        Context string
    """
    line = lines[line_idx]

    # Get some lines before and after if the current line is short
    context_lines = [line]

    if len(line) < context_chars and line_idx > 0:
        context_lines.insert(0, lines[line_idx - 1])

    if len(line) < context_chars and line_idx < len(lines) - 1:
        context_lines.append(lines[line_idx + 1])

    context = ' '.join(l.strip() for l in context_lines)

    # Truncate if too long
    if len(context) > context_chars * 2:
        context = context[:context_chars * 2] + '...'

    return context


def extract_from_markdown(file_path: str) -> List[Citation]:
    """Extract citations with DOIs from a Markdown file.

    Args:
        file_path: Path to the Markdown file (.md or .qmd)

    Returns:
        List of Citation objects
    """
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    if path.suffix.lower() not in ['.md', '.qmd', '.markdown']:
        raise ValueError(f"Expected Markdown file, got: {path.suffix}")

    content = path.read_text(encoding='utf-8')
    lines = content.split('\n')

    citations = []
    seen_dois = set()  # Track DOIs to avoid duplicates

    for line_idx, line in enumerate(lines):
        # Try each DOI pattern
        for pattern in DOI_PATTERNS:
            for match in re.finditer(pattern, line):
                # Get the DOI (last group in the match)
                groups = match.groups()
                doi = clean_doi(groups[-1])

                # Skip if we've already seen this DOI
                if doi in seen_dois:
                    continue
                seen_dois.add(doi)

                # Get citation text if available (first group for link patterns)
                text = groups[0] if len(groups) > 1 else ""

                # Extract author and year from citation text
                claimed_author, claimed_year = extract_author_year(text)

                citation = Citation(
                    doi=doi,
                    text=text,
                    context=get_context(lines, line_idx),
                    line_number=line_idx + 1,  # 1-indexed
                    file_path=str(path),
                    claimed_author=claimed_author,
                    claimed_year=claimed_year,
                )

                citations.append(citation)

    return citations


def extract_from_directory(
    directory: str,
    extensions: List[str] = ['.md', '.qmd'],
    recursive: bool = True
) -> List[Citation]:
    """Extract citations from all Markdown files in a directory.

    Args:
        directory: Path to directory
        extensions: File extensions to process
        recursive: Whether to search subdirectories

    Returns:
        List of Citation objects from all files
    """
    dir_path = Path(directory)

    if not dir_path.is_dir():
        raise NotADirectoryError(f"Not a directory: {directory}")

    all_citations = []

    pattern = '**/*' if recursive else '*'

    for ext in extensions:
        for file_path in dir_path.glob(f'{pattern}{ext}'):
            try:
                citations = extract_from_markdown(str(file_path))
                all_citations.extend(citations)
            except Exception as e:
                print(f"Warning: Error processing {file_path}: {e}")

    return all_citations
