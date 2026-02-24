"""Extract citations from BibTeX files."""

import re
from pathlib import Path
from typing import List, Optional

try:
    import bibtexparser
    from bibtexparser.bparser import BibTexParser
    HAS_BIBTEX = True
except ImportError:
    HAS_BIBTEX = False

from .markdown import Citation


def extract_from_bibtex(file_path: str) -> List[Citation]:
    """Extract citations with DOIs from a BibTeX file.

    Args:
        file_path: Path to the BibTeX file (.bib)

    Returns:
        List of Citation objects
    """
    if not HAS_BIBTEX:
        raise ImportError(
            "bibtexparser is required for BibTeX support. "
            "Install with: pip install bibtexparser"
        )

    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    if path.suffix.lower() != '.bib':
        raise ValueError(f"Expected BibTeX file (.bib), got: {path.suffix}")

    content = path.read_text(encoding='utf-8')

    # Parse BibTeX
    parser = BibTexParser(common_strings=True)
    bib_database = bibtexparser.loads(content, parser=parser)

    citations = []

    for entry in bib_database.entries:
        # Skip entries without DOI
        doi = entry.get('doi', '')
        if not doi:
            continue

        # Clean DOI (remove URL prefix if present)
        doi = doi.replace('https://doi.org/', '').replace('http://doi.org/', '')
        doi = doi.strip()

        # Extract author
        author_raw = entry.get('author', '')
        # BibTeX uses "and" to separate authors
        first_author = author_raw.split(' and ')[0].strip() if author_raw else None
        # Get last name (usually first part or after comma)
        if first_author and ',' in first_author:
            claimed_author = first_author.split(',')[0].strip()
        elif first_author:
            # Assume "First Last" format
            parts = first_author.split()
            claimed_author = parts[-1] if parts else None
        else:
            claimed_author = None

        # Extract year
        year_str = entry.get('year', '')
        try:
            claimed_year = int(year_str) if year_str else None
        except ValueError:
            claimed_year = None

        # Build citation text
        title = entry.get('title', '').strip('{}')
        journal = entry.get('journal', entry.get('booktitle', ''))

        text = f"{first_author or 'Unknown'}"
        if claimed_year:
            text += f", {claimed_year}"

        citation = Citation(
            doi=doi,
            text=text,
            context=f"{title[:100]}..." if len(title) > 100 else title,
            line_number=0,  # BibTeX doesn't have meaningful line numbers
            file_path=str(path),
            claimed_author=claimed_author,
            claimed_year=claimed_year,
            claimed_journal=journal,
        )

        citations.append(citation)

    return citations


def extract_dois_only(file_path: str) -> List[str]:
    """Extract just the DOIs from a BibTeX file.

    Args:
        file_path: Path to the BibTeX file

    Returns:
        List of DOI strings
    """
    citations = extract_from_bibtex(file_path)
    return [c.doi for c in citations]
