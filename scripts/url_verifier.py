#!/usr/bin/env python3
"""
URL Verifier Module (Phase 1)

Tests URL/DOI resolution and captures redirect chains.

Part of the Four-Phase Citation Verification Pipeline.
"""

import re
import time
import json
import asyncio
import aiohttp
from pathlib import Path
from dataclasses import dataclass, field, asdict
from typing import List, Optional, Dict, Tuple
from urllib.parse import urlparse
from enum import Enum


class URLStatus(Enum):
    """URL verification status codes."""
    OK = "ok"
    BROKEN = "broken_404"
    FORBIDDEN = "forbidden_403"
    REDIRECT = "redirect"
    TIMEOUT = "timeout"
    SSL_ERROR = "ssl_error"
    CONNECTION_ERROR = "connection_error"
    UNKNOWN_ERROR = "unknown_error"


@dataclass
class RedirectHop:
    """Represents a single hop in a redirect chain."""
    url: str
    status_code: int
    headers: Dict[str, str] = field(default_factory=dict)


@dataclass
class URLVerificationResult:
    """Result of URL verification."""
    original_url: str
    final_url: str
    status: URLStatus
    status_code: Optional[int]
    redirect_chain: List[RedirectHop] = field(default_factory=list)
    content_type: Optional[str] = None
    page_title: Optional[str] = None
    error_message: Optional[str] = None
    response_time_ms: Optional[float] = None

    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization."""
        result = asdict(self)
        result['status'] = self.status.value
        return result

    @property
    def is_valid(self) -> bool:
        """Check if URL resolved successfully."""
        return self.status in [URLStatus.OK, URLStatus.REDIRECT]

    @property
    def is_broken(self) -> bool:
        """Check if URL is broken."""
        return self.status == URLStatus.BROKEN

    @property
    def is_doi(self) -> bool:
        """Check if URL is a DOI link."""
        return 'doi.org' in self.original_url.lower()

    @property
    def publisher_domain(self) -> Optional[str]:
        """Extract publisher domain from final URL."""
        if self.final_url:
            parsed = urlparse(self.final_url)
            return parsed.netloc
        return None


class URLVerifier:
    """
    Verifies URL/DOI resolution.

    Usage:
        verifier = URLVerifier()
        result = await verifier.verify_url("https://doi.org/10.1001/...")
        # or batch processing
        results = await verifier.verify_batch(urls)
    """

    # DOI redirect patterns
    DOI_PUBLISHER_PATTERNS = {
        '10.1001': ('JAMA Network', 'jamanetwork.com'),
        '10.1016': ('Elsevier', 'sciencedirect.com'),
        '10.1038': ('Nature', 'nature.com'),
        '10.1056': ('NEJM', 'nejm.org'),
        '10.1093': ('Oxford Academic', 'academic.oup.com'),
        '10.1136': ('BMJ', 'bmj.com'),
        '10.1186': ('BioMed Central', 'biomedcentral.com'),
        '10.1371': ('PLOS', 'journals.plos.org'),
        '10.1128': ('ASM', 'journals.asm.org'),
        '10.1017': ('Cambridge', 'cambridge.org'),
    }

    # User agent to avoid bot blocking
    USER_AGENT = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )

    def __init__(
        self,
        timeout: int = 30,
        max_redirects: int = 10,
        retry_attempts: int = 3,
        retry_delay: float = 1.0
    ):
        """
        Initialize URL verifier.

        Args:
            timeout: Request timeout in seconds
            max_redirects: Maximum number of redirects to follow
            retry_attempts: Number of retry attempts for failed requests
            retry_delay: Delay between retries in seconds
        """
        self.timeout = timeout
        self.max_redirects = max_redirects
        self.retry_attempts = retry_attempts
        self.retry_delay = retry_delay

    async def verify_url(self, url: str) -> URLVerificationResult:
        """
        Verify a single URL.

        Args:
            url: URL to verify

        Returns:
            URLVerificationResult with verification details
        """
        start_time = time.time()
        redirect_chain = []
        current_url = url
        final_url = url
        status_code = None
        content_type = None
        page_title = None
        error_message = None
        status = URLStatus.UNKNOWN_ERROR

        headers = {'User-Agent': self.USER_AGENT}

        connector = aiohttp.TCPConnector(ssl=False)  # Disable SSL verification for testing
        timeout_config = aiohttp.ClientTimeout(total=self.timeout)

        try:
            async with aiohttp.ClientSession(
                connector=connector,
                timeout=timeout_config,
                headers=headers
            ) as session:
                for attempt in range(self.retry_attempts):
                    try:
                        async with session.get(
                            current_url,
                            allow_redirects=False
                        ) as response:
                            status_code = response.status

                            # Track redirect
                            hop = RedirectHop(
                                url=current_url,
                                status_code=status_code,
                                headers=dict(response.headers)
                            )
                            redirect_chain.append(hop)

                            # Handle redirects
                            if status_code in [301, 302, 303, 307, 308]:
                                location = response.headers.get('Location', '')
                                if location:
                                    # Handle relative URLs
                                    if location.startswith('/'):
                                        parsed = urlparse(current_url)
                                        location = f"{parsed.scheme}://{parsed.netloc}{location}"
                                    current_url = location

                                    if len(redirect_chain) < self.max_redirects:
                                        continue
                                    else:
                                        status = URLStatus.REDIRECT
                                        error_message = "Max redirects exceeded"
                                        break

                            # Final response
                            final_url = str(response.url)
                            content_type = response.headers.get('Content-Type', '')

                            if status_code == 200:
                                status = URLStatus.OK
                                # Try to extract page title
                                if 'text/html' in content_type.lower():
                                    try:
                                        html = await response.text()
                                        title_match = re.search(
                                            r'<title[^>]*>([^<]+)</title>',
                                            html,
                                            re.IGNORECASE
                                        )
                                        if title_match:
                                            page_title = title_match.group(1).strip()
                                    except Exception:
                                        pass
                            elif status_code == 404:
                                status = URLStatus.BROKEN
                            elif status_code == 403:
                                status = URLStatus.FORBIDDEN
                            else:
                                status = URLStatus.OK if status_code < 400 else URLStatus.UNKNOWN_ERROR

                            break  # Success, exit retry loop

                    except asyncio.TimeoutError:
                        if attempt < self.retry_attempts - 1:
                            await asyncio.sleep(self.retry_delay)
                            continue
                        status = URLStatus.TIMEOUT
                        error_message = f"Request timed out after {self.timeout}s"

                    except aiohttp.ClientSSLError as e:
                        status = URLStatus.SSL_ERROR
                        error_message = str(e)
                        break

                    except aiohttp.ClientConnectorError as e:
                        if attempt < self.retry_attempts - 1:
                            await asyncio.sleep(self.retry_delay)
                            continue
                        status = URLStatus.CONNECTION_ERROR
                        error_message = str(e)

                    except Exception as e:
                        if attempt < self.retry_attempts - 1:
                            await asyncio.sleep(self.retry_delay)
                            continue
                        status = URLStatus.UNKNOWN_ERROR
                        error_message = str(e)

        except Exception as e:
            status = URLStatus.UNKNOWN_ERROR
            error_message = str(e)

        response_time = (time.time() - start_time) * 1000

        return URLVerificationResult(
            original_url=url,
            final_url=final_url,
            status=status,
            status_code=status_code,
            redirect_chain=redirect_chain,
            content_type=content_type,
            page_title=page_title,
            error_message=error_message,
            response_time_ms=response_time
        )

    async def verify_batch(
        self,
        urls: List[str],
        concurrency: int = 10,
        progress_callback=None
    ) -> List[URLVerificationResult]:
        """
        Verify multiple URLs concurrently.

        Args:
            urls: List of URLs to verify
            concurrency: Maximum concurrent requests
            progress_callback: Optional callback function(completed, total)

        Returns:
            List of URLVerificationResult objects
        """
        semaphore = asyncio.Semaphore(concurrency)
        results = []
        completed = 0

        async def verify_with_semaphore(url: str) -> URLVerificationResult:
            nonlocal completed
            async with semaphore:
                result = await self.verify_url(url)
                completed += 1
                if progress_callback:
                    progress_callback(completed, len(urls))
                return result

        tasks = [verify_with_semaphore(url) for url in urls]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Handle exceptions
        final_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                final_results.append(URLVerificationResult(
                    original_url=urls[i],
                    final_url=urls[i],
                    status=URLStatus.UNKNOWN_ERROR,
                    status_code=None,
                    error_message=str(result)
                ))
            else:
                final_results.append(result)

        return final_results

    def get_expected_publisher(self, doi_url: str) -> Optional[Tuple[str, str]]:
        """
        Get expected publisher for a DOI.

        Args:
            doi_url: DOI URL

        Returns:
            Tuple of (publisher_name, expected_domain) or None
        """
        for prefix, info in self.DOI_PUBLISHER_PATTERNS.items():
            if prefix in doi_url:
                return info
        return None


def export_results(results: List[URLVerificationResult], output_path: str) -> None:
    """
    Export verification results to JSON.

    Args:
        results: List of URLVerificationResult objects
        output_path: Path for output JSON file
    """
    # Calculate statistics
    stats = {
        'total': len(results),
        'ok': sum(1 for r in results if r.status == URLStatus.OK),
        'broken': sum(1 for r in results if r.status == URLStatus.BROKEN),
        'forbidden': sum(1 for r in results if r.status == URLStatus.FORBIDDEN),
        'timeout': sum(1 for r in results if r.status == URLStatus.TIMEOUT),
        'ssl_error': sum(1 for r in results if r.status == URLStatus.SSL_ERROR),
        'connection_error': sum(1 for r in results if r.status == URLStatus.CONNECTION_ERROR),
        'other_error': sum(1 for r in results if r.status == URLStatus.UNKNOWN_ERROR),
    }

    data = {
        'statistics': stats,
        'results': [r.to_dict() for r in results]
    }

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


async def main():
    """Example usage of the URL verifier."""
    import argparse

    parser = argparse.ArgumentParser(description='Verify URLs from citation extraction')
    parser.add_argument('input', help='Input JSON file from citation_extractor.py')
    parser.add_argument('-o', '--output', default='url_verification.json', help='Output JSON file')
    parser.add_argument('-c', '--concurrency', type=int, default=10, help='Max concurrent requests')

    args = parser.parse_args()

    # Load citations
    with open(args.input, 'r', encoding='utf-8') as f:
        data = json.load(f)

    urls = [c['url'] for c in data['citations']]

    print(f"Verifying {len(urls)} URLs...")

    verifier = URLVerifier()

    def progress(completed, total):
        print(f"\rProgress: {completed}/{total}", end='', flush=True)

    results = await verifier.verify_batch(urls, concurrency=args.concurrency, progress_callback=progress)

    print()  # New line after progress

    # Export results
    export_results(results, args.output)

    # Print summary
    ok_count = sum(1 for r in results if r.status == URLStatus.OK)
    broken_count = sum(1 for r in results if r.status == URLStatus.BROKEN)

    print(f"\nResults:")
    print(f"  OK: {ok_count}")
    print(f"  Broken: {broken_count}")
    print(f"  Other: {len(results) - ok_count - broken_count}")
    print(f"\nExported to: {args.output}")


if __name__ == '__main__':
    asyncio.run(main())
