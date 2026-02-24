"""CrossRef API integration for metadata retrieval."""

import time
from dataclasses import dataclass, field
from typing import List, Optional
from urllib.parse import quote

import requests


@dataclass
class Author:
    """Author information from CrossRef."""

    family: str  # Last name
    given: Optional[str] = None  # First name
    orcid: Optional[str] = None

    def __str__(self) -> str:
        if self.given:
            return f"{self.given} {self.family}"
        return self.family


@dataclass
class CrossRefMetadata:
    """Metadata retrieved from CrossRef API."""

    doi: str
    title: str
    authors: List[Author] = field(default_factory=list)
    year: Optional[int] = None
    month: Optional[int] = None
    day: Optional[int] = None
    journal: Optional[str] = None
    publisher: Optional[str] = None
    type: Optional[str] = None  # journal-article, book-chapter, etc.
    issn: Optional[List[str]] = None
    url: Optional[str] = None

    # Raw response for debugging
    raw: Optional[dict] = None

    @property
    def first_author(self) -> Optional[str]:
        """Get first author's last name."""
        if self.authors:
            return self.authors[0].family
        return None

    @property
    def author_string(self) -> str:
        """Get formatted author string."""
        if not self.authors:
            return "Unknown"

        if len(self.authors) == 1:
            return str(self.authors[0])
        elif len(self.authors) == 2:
            return f"{self.authors[0]} and {self.authors[1]}"
        else:
            return f"{self.authors[0]} et al."


# Rate limiting for CrossRef API
_last_request_time = 0
MIN_REQUEST_INTERVAL = 0.05  # CrossRef allows ~50 req/sec in polite pool


def _rate_limit():
    """Ensure we don't exceed rate limits."""
    global _last_request_time
    elapsed = time.time() - _last_request_time
    if elapsed < MIN_REQUEST_INTERVAL:
        time.sleep(MIN_REQUEST_INTERVAL - elapsed)
    _last_request_time = time.time()


def get_crossref_metadata(doi: str, timeout: int = 15) -> Optional[CrossRefMetadata]:
    """Fetch metadata for a DOI from CrossRef API.

    Args:
        doi: The DOI to look up (without URL prefix)
        timeout: Request timeout in seconds

    Returns:
        CrossRefMetadata if found, None otherwise
    """
    _rate_limit()

    # Clean the DOI
    doi = doi.strip()
    if doi.startswith('http'):
        doi = doi.split('doi.org/')[-1]

    # URL-encode the DOI
    encoded_doi = quote(doi, safe='')
    url = f"https://api.crossref.org/works/{encoded_doi}"

    try:
        response = requests.get(
            url,
            timeout=timeout,
            headers={
                'User-Agent': 'CitationVerificationToolkit/1.0 (mailto:verify@example.com)'
            }
        )

        if response.status_code == 404:
            return None

        response.raise_for_status()

        data = response.json()
        message = data.get('message', {})

        # Parse authors
        authors = []
        for author_data in message.get('author', []):
            author = Author(
                family=author_data.get('family', 'Unknown'),
                given=author_data.get('given'),
                orcid=author_data.get('ORCID'),
            )
            authors.append(author)

        # Parse publication date
        date_parts = None
        for date_field in ['published-print', 'published-online', 'published', 'created']:
            if date_field in message:
                date_parts = message[date_field].get('date-parts', [[]])[0]
                if date_parts:
                    break

        year = date_parts[0] if date_parts and len(date_parts) > 0 else None
        month = date_parts[1] if date_parts and len(date_parts) > 1 else None
        day = date_parts[2] if date_parts and len(date_parts) > 2 else None

        # Parse title (can be a list)
        title_list = message.get('title', [])
        title = title_list[0] if title_list else 'Unknown Title'

        # Parse journal (container-title)
        journal_list = message.get('container-title', [])
        journal = journal_list[0] if journal_list else None

        return CrossRefMetadata(
            doi=doi,
            title=title,
            authors=authors,
            year=year,
            month=month,
            day=day,
            journal=journal,
            publisher=message.get('publisher'),
            type=message.get('type'),
            issn=message.get('ISSN'),
            url=message.get('URL'),
            raw=message,
        )

    except requests.exceptions.RequestException:
        return None
    except (KeyError, ValueError, IndexError):
        return None


def compare_metadata(
    claimed_author: Optional[str],
    claimed_year: Optional[int],
    actual: CrossRefMetadata
) -> dict:
    """Compare claimed citation metadata against actual CrossRef data.

    Args:
        claimed_author: Author name from citation (e.g., "Smith")
        claimed_year: Publication year from citation
        actual: CrossRef metadata

    Returns:
        Dict with comparison results
    """
    results = {
        'author_match': None,
        'year_match': None,
        'author_claimed': claimed_author,
        'author_actual': actual.first_author,
        'year_claimed': claimed_year,
        'year_actual': actual.year,
        'issues': [],
    }

    # Compare author (case-insensitive, partial match)
    if claimed_author and actual.first_author:
        claimed_lower = claimed_author.lower()
        actual_lower = actual.first_author.lower()

        # Check if claimed author matches any author's last name
        author_match = False
        for author in actual.authors:
            if claimed_lower in author.family.lower():
                author_match = True
                break

        results['author_match'] = author_match
        if not author_match:
            results['issues'].append(
                f"Author mismatch: claimed '{claimed_author}', "
                f"actual first author '{actual.first_author}'"
            )

    # Compare year (allow ±1 year tolerance for Dec/Jan publishing)
    if claimed_year and actual.year:
        year_diff = abs(claimed_year - actual.year)
        results['year_match'] = year_diff <= 1

        if year_diff > 1:
            results['issues'].append(
                f"Year mismatch: claimed {claimed_year}, actual {actual.year}"
            )
        elif year_diff == 1:
            results['issues'].append(
                f"Year off by 1: claimed {claimed_year}, actual {actual.year} (minor)"
            )

    return results


def batch_get_metadata(
    dois: List[str],
    timeout: int = 15,
    progress_callback=None
) -> dict[str, Optional[CrossRefMetadata]]:
    """Fetch metadata for multiple DOIs.

    Args:
        dois: List of DOIs to look up
        timeout: Request timeout per DOI
        progress_callback: Optional callback(current, total)

    Returns:
        Dict mapping DOI to CrossRefMetadata (or None if not found)
    """
    results = {}

    for i, doi in enumerate(dois):
        results[doi] = get_crossref_metadata(doi, timeout)

        if progress_callback:
            progress_callback(i + 1, len(dois))

    return results
