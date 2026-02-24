"""DOI resolution and existence checking."""

import time
from dataclasses import dataclass
from typing import Optional
from urllib.parse import quote

import requests


@dataclass
class DOIResolutionResult:
    """Result of DOI resolution check."""

    doi: str
    exists: bool
    status_code: int
    redirect_url: Optional[str] = None
    error: Optional[str] = None


# Rate limiting
_last_request_time = 0
MIN_REQUEST_INTERVAL = 0.1  # seconds between requests


def _rate_limit():
    """Ensure we don't make requests too quickly."""
    global _last_request_time
    elapsed = time.time() - _last_request_time
    if elapsed < MIN_REQUEST_INTERVAL:
        time.sleep(MIN_REQUEST_INTERVAL - elapsed)
    _last_request_time = time.time()


def check_doi_exists(doi: str, timeout: int = 10) -> DOIResolutionResult:
    """Check if a DOI exists by attempting to resolve it.

    Uses HEAD request to doi.org to check resolution without
    downloading the full page.

    Args:
        doi: The DOI to check (without URL prefix)
        timeout: Request timeout in seconds

    Returns:
        DOIResolutionResult with existence status
    """
    _rate_limit()

    # Clean the DOI
    doi = doi.strip()
    if doi.startswith('http'):
        # Extract DOI from URL
        doi = doi.split('doi.org/')[-1]

    # URL-encode the DOI for the request
    encoded_doi = quote(doi, safe='')
    url = f"https://doi.org/{encoded_doi}"

    try:
        # Use HEAD request to avoid downloading content
        response = requests.head(
            url,
            allow_redirects=True,
            timeout=timeout,
            headers={
                'User-Agent': 'CitationVerificationToolkit/1.0 (mailto:verify@example.com)'
            }
        )

        # DOI exists if we get a successful response or redirect
        exists = response.status_code in [200, 301, 302, 303, 307, 308]

        # Get final redirect URL if available
        redirect_url = response.url if response.url != url else None

        return DOIResolutionResult(
            doi=doi,
            exists=exists,
            status_code=response.status_code,
            redirect_url=redirect_url,
        )

    except requests.exceptions.Timeout:
        return DOIResolutionResult(
            doi=doi,
            exists=False,
            status_code=0,
            error="Request timed out"
        )

    except requests.exceptions.RequestException as e:
        return DOIResolutionResult(
            doi=doi,
            exists=False,
            status_code=0,
            error=str(e)
        )


def resolve_doi(doi: str, timeout: int = 10) -> Optional[str]:
    """Resolve a DOI to its final URL.

    Args:
        doi: The DOI to resolve
        timeout: Request timeout in seconds

    Returns:
        The final URL after resolution, or None if resolution fails
    """
    result = check_doi_exists(doi, timeout)

    if result.exists and result.redirect_url:
        return result.redirect_url

    return None


def batch_check_dois(
    dois: list[str],
    timeout: int = 10,
    progress_callback=None
) -> list[DOIResolutionResult]:
    """Check multiple DOIs for existence.

    Args:
        dois: List of DOIs to check
        timeout: Request timeout per DOI
        progress_callback: Optional callback(current, total) for progress

    Returns:
        List of DOIResolutionResult objects
    """
    results = []

    for i, doi in enumerate(dois):
        result = check_doi_exists(doi, timeout)
        results.append(result)

        if progress_callback:
            progress_callback(i + 1, len(dois))

    return results
