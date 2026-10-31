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


HANDLE_API = "https://doi.org/api/handles/{doi}"
USER_AGENT = "CitationVerificationToolkit/1.0 (https://github.com/BryanTegomoh/citation-audit)"


def _clean_doi(doi: str) -> str:
    doi = doi.strip()
    if doi.lower().startswith("http") and "doi.org/" in doi:
        doi = doi.split("doi.org/", 1)[-1]
    if doi.lower().startswith("doi:"):
        doi = doi[4:].strip()
    return doi


def check_doi_exists(doi: str, timeout: int = 10) -> DOIResolutionResult:
    """Check if a DOI exists in the DOI system.

    Queries the doi.org Handle API, which answers from the DOI registry
    itself (Crossref, DataCite, mEDRA, ...). We deliberately do NOT follow
    the redirect to the publisher: many medical publishers (NEJM, Elsevier,
    Wiley) return 403 to automated clients, which previously made real
    DOIs look fabricated.

    Handle API responseCode: 1 = exists, 100 = handle not found.

    Args:
        doi: The DOI to check (bare, doi: prefixed, or a doi.org URL)
        timeout: Request timeout in seconds

    Returns:
        DOIResolutionResult with existence status. redirect_url is the
        registered landing-page URL when the registry provides one.
    """
    _rate_limit()
    doi = _clean_doi(doi)
    url = HANDLE_API.format(doi=quote(doi, safe="/"))

    try:
        response = requests.get(
            url,
            params={"type": "URL"},
            timeout=timeout,
            headers={"User-Agent": USER_AGENT, "Accept": "application/json"},
        )
    except requests.exceptions.Timeout:
        return DOIResolutionResult(doi=doi, exists=False, status_code=0,
                                   error="Request timed out")
    except requests.exceptions.RequestException as e:
        return DOIResolutionResult(doi=doi, exists=False, status_code=0,
                                   error=str(e))

    try:
        data = response.json()
    except ValueError:
        data = {}
    code = data.get("responseCode")

    if code == 1:
        redirect_url = None
        for value in data.get("values", []):
            if value.get("type") == "URL":
                redirect_url = value.get("data", {}).get("value")
                break
        return DOIResolutionResult(doi=doi, exists=True, status_code=200,
                                   redirect_url=redirect_url)

    if code == 100 or response.status_code == 404:
        # No `error`: callers treat error as "could not verify".
        return DOIResolutionResult(doi=doi, exists=False, status_code=404)

    # Anything else (rate limit, server error) is unknown, not "fabricated".
    return DOIResolutionResult(
        doi=doi,
        exists=False,
        status_code=response.status_code,
        error=f"DOI registry lookup failed (HTTP {response.status_code}, responseCode {code})",
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
