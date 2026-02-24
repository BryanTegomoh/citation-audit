"""Extract DOIs from plain text files."""

import re
from pathlib import Path
from typing import List

from .markdown import Citation, clean_doi


# DOI pattern for plain text (one DOI per line or embedded in text)
DOI_PATTERN = re.compile(
    r'(?:https?://(?:dx\.)?doi\.org/)?'  # Optional URL prefix
    r'(?:doi:)?'  # Optional doi: prefix
    r'\s*'
    r'(10\.\d{4,}/[^\s,;\]\)]+)',  # The actual DOI
    re.IGNORECASE
)


def extract_from_plaintext(file_path: str) -> List[Citation]:
    """Extract DOIs from a plain text file.

    Expects one DOI per line, but will also find DOIs embedded in text.
    Lines starting with # are treated as comments.

    Args:
        file_path: Path to the text file

    Returns:
        List of Citation objects (with minimal metadata)
    """
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    content = path.read_text(encoding='utf-8')
    lines = content.split('\n')

    citations = []
    seen_dois = set()

    for line_idx, line in enumerate(lines):
        # Skip comments and empty lines
        line = line.strip()
        if not line or line.startswith('#'):
            continue

        # Find DOIs in this line
        for match in DOI_PATTERN.finditer(line):
            doi = clean_doi(match.group(1))

            # Skip duplicates
            if doi in seen_dois:
                continue
            seen_dois.add(doi)

            citation = Citation(
                doi=doi,
                text="",  # No citation text in plain DOI lists
                context=line[:200] if len(line) > 200 else line,
                line_number=line_idx + 1,
                file_path=str(path),
            )

            citations.append(citation)

    return citations


def extract_from_string(text: str) -> List[str]:
    """Extract DOIs from a string.

    Args:
        text: Text containing DOIs

    Returns:
        List of DOI strings
    """
    dois = []
    seen = set()

    for match in DOI_PATTERN.finditer(text):
        doi = clean_doi(match.group(1))
        if doi not in seen:
            seen.add(doi)
            dois.append(doi)

    return dois
