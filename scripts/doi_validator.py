#!/usr/bin/env python3
"""
DOI Validator Module (Phase 0)

Validates DOI existence in CrossRef registry BEFORE URL resolution.
Distinguishes between broken links (transcription errors) and fabricated DOIs.

Part of the Five-Phase Citation Verification Pipeline.
"""

import re
import json
import asyncio
import aiohttp
from pathlib import Path
from dataclasses import dataclass, field, asdict
from typing import List, Optional, Dict, Tuple
from enum import Enum


class DOIStatus(Enum):
    """DOI validation status codes."""
    EXISTS = "exists"
    FABRICATED = "fabricated"
    INVALID_FORMAT = "invalid_format"
    API_ERROR = "api_error"
    NOT_DOI = "not_doi"


@dataclass
class DOIValidationResult:
    """Result of DOI existence validation."""
    original_url: str
    extracted_doi: Optional[str]
    status: DOIStatus
    publisher: Optional[str] = None
    title: Optional[str] = None
    crossref_metadata: Optional[Dict] = None
    error_message: Optional[str] = None
    response_time_ms: Optional[float] = None

    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization."""
        result = asdict(self)
        result['status'] = self.status.value
        return result

    @property
    def is_valid_doi(self) -> bool:
        """Check if DOI exists in registry."""
        return self.status == DOIStatus.EXISTS

    @property
    def is_fabricated(self) -> bool:
        """Check if DOI appears fabricated."""
        return self.status == DOIStatus.FABRICATED

    @property
    def has_valid_format(self) -> bool:
        """Check if URL contains valid DOI format."""
        return self.extracted_doi is not None


# Known DOI prefixes and their publishers
DOI_PUBLISHER_PREFIXES = {
    '10.1001': 'JAMA Network',
    '10.1016': 'Elsevier',
    '10.1038': 'Nature',
    '10.1056': 'NEJM',
    '10.1093': 'Oxford Academic',
    '10.1136': 'BMJ',
    '10.1186': 'BioMed Central',
    '10.1371': 'PLOS',
    '10.1128': 'ASM',
    '10.1017': 'Cambridge',
    '10.1002': 'Wiley',
    '10.1177': 'SAGE',
    '10.1097': 'Lippincott Williams & Wilkins',
    '10.1007': 'Springer',
    '10.1073': 'PNAS',
    '10.1126': 'Science/AAAS',
    '10.1161': 'AHA Journals',
    '10.1164': 'ATS Journals',
    '10.1183': 'ERS Journals',
    '10.1200': 'ASCO',
    '10.1210': 'Endocrine Society',
    '10.1212': 'AAN/Neurology',
    '10.1148': 'RSNA Radiology',
    '10.2147': 'Dove Press',
    '10.2196': 'JMIR',
    '10.3389': 'Frontiers',
    '10.3390': 'MDPI',
    '10.4103': 'Medknow',
}


class DOIValidator:
    """
    Validates DOI existence via CrossRef API.

    Usage:
        validator = DOIValidator()
        result = await validator.validate_doi("10.1001/jamainternmed.2021.2626")
        # or from URL
        result = await validator.validate_url("https://doi.org/10.1001/jamainternmed.2021.2626")
    """

    CROSSREF_API = "https://api.crossref.org/works"
    DOI_PATTERN = re.compile(r'10\.\d{4,}/[^\s\)]+')

    def __init__(self, timeout: int = 30, email: str = "verification@example.com"):
        """
        Initialize DOI validator.

        Args:
            timeout: Request timeout in seconds
            email: Email for CrossRef API (polite pool)
        """
        self.timeout = timeout
        self.email = email

    def extract_doi(self, url: str) -> Optional[str]:
        """
        Extract DOI from URL.

        Args:
            url: URL that may contain a DOI

        Returns:
            Extracted DOI or None
        """
        match = self.DOI_PATTERN.search(url)
        if match:
            doi = match.group(0).rstrip('/')
            # Clean common trailing characters
            doi = re.sub(r'[.,;:]+$', '', doi)
            return doi
        return None

    def get_expected_publisher(self, doi: str) -> Optional[str]:
        """
        Get expected publisher based on DOI prefix.

        Args:
            doi: DOI string

        Returns:
            Publisher name or None
        """
        for prefix, publisher in DOI_PUBLISHER_PREFIXES.items():
            if doi.startswith(prefix):
                return publisher
        return None

    def has_valid_format(self, doi: str) -> bool:
        """
        Check if DOI has valid format.

        Args:
            doi: DOI string

        Returns:
            True if format is valid
        """
        # Basic DOI format: 10.prefix/suffix
        return bool(re.match(r'^10\.\d{4,}/\S+$', doi))

    async def validate_doi(self, doi: str) -> DOIValidationResult:
        """
        Validate a single DOI against CrossRef.

        Args:
            doi: DOI to validate (without https://doi.org/ prefix)

        Returns:
            DOIValidationResult with validation details
        """
        import time
        start_time = time.time()

        # Construct fake URL for result object
        url = f"https://doi.org/{doi}"

        # Validate format
        if not self.has_valid_format(doi):
            return DOIValidationResult(
                original_url=url,
                extracted_doi=doi,
                status=DOIStatus.INVALID_FORMAT,
                error_message="DOI format invalid"
            )

        # Query CrossRef
        api_url = f"{self.CROSSREF_API}/{doi}"
        headers = {
            'User-Agent': f'CitationVerifier/1.0 (mailto:{self.email})'
        }

        try:
            timeout_config = aiohttp.ClientTimeout(total=self.timeout)
            async with aiohttp.ClientSession(timeout=timeout_config) as session:
                async with session.get(api_url, headers=headers) as response:
                    response_time = (time.time() - start_time) * 1000

                    if response.status == 200:
                        data = await response.json()
                        message = data.get('message', {})

                        # Extract metadata
                        title = message.get('title', [None])[0]
                        publisher = message.get('publisher')
                        container = message.get('container-title', [None])[0]

                        return DOIValidationResult(
                            original_url=url,
                            extracted_doi=doi,
                            status=DOIStatus.EXISTS,
                            publisher=publisher or self.get_expected_publisher(doi),
                            title=title,
                            crossref_metadata={
                                'title': title,
                                'publisher': publisher,
                                'journal': container,
                                'type': message.get('type')
                            },
                            response_time_ms=response_time
                        )

                    elif response.status == 404:
                        # DOI does not exist - this is the key finding
                        return DOIValidationResult(
                            original_url=url,
                            extracted_doi=doi,
                            status=DOIStatus.FABRICATED,
                            publisher=self.get_expected_publisher(doi),
                            error_message="DOI not found in CrossRef registry",
                            response_time_ms=response_time
                        )

                    else:
                        return DOIValidationResult(
                            original_url=url,
                            extracted_doi=doi,
                            status=DOIStatus.API_ERROR,
                            error_message=f"CrossRef API returned {response.status}",
                            response_time_ms=response_time
                        )

        except asyncio.TimeoutError:
            return DOIValidationResult(
                original_url=url,
                extracted_doi=doi,
                status=DOIStatus.API_ERROR,
                error_message=f"CrossRef API timeout after {self.timeout}s"
            )

        except Exception as e:
            return DOIValidationResult(
                original_url=url,
                extracted_doi=doi,
                status=DOIStatus.API_ERROR,
                error_message=str(e)
            )

    async def validate_url(self, url: str) -> DOIValidationResult:
        """
        Extract DOI from URL and validate.

        Args:
            url: URL that may contain a DOI

        Returns:
            DOIValidationResult
        """
        doi = self.extract_doi(url)

        if not doi:
            return DOIValidationResult(
                original_url=url,
                extracted_doi=None,
                status=DOIStatus.NOT_DOI,
                error_message="No DOI found in URL"
            )

        result = await self.validate_doi(doi)
        result.original_url = url
        return result

    async def validate_batch(
        self,
        urls: List[str],
        concurrency: int = 5,
        progress_callback=None
    ) -> List[DOIValidationResult]:
        """
        Validate multiple URLs for DOI existence.

        Args:
            urls: List of URLs to validate
            concurrency: Maximum concurrent API requests
            progress_callback: Optional callback function(completed, total)

        Returns:
            List of DOIValidationResult objects
        """
        semaphore = asyncio.Semaphore(concurrency)
        completed = 0

        async def validate_with_limit(url: str) -> DOIValidationResult:
            nonlocal completed
            async with semaphore:
                # Rate limiting for CrossRef API
                await asyncio.sleep(0.2)
                result = await self.validate_url(url)
                completed += 1
                if progress_callback:
                    progress_callback(completed, len(urls))
                return result

        tasks = [validate_with_limit(url) for url in urls]
        return await asyncio.gather(*tasks)


def analyze_fabrication_patterns(results: List[DOIValidationResult]) -> Dict:
    """
    Analyze patterns in fabricated DOIs.

    Args:
        results: List of validation results

    Returns:
        Analysis dictionary
    """
    fabricated = [r for r in results if r.is_fabricated]

    # Analyze by publisher prefix
    by_publisher = {}
    for r in fabricated:
        if r.extracted_doi:
            prefix = r.extracted_doi[:7] if len(r.extracted_doi) > 7 else r.extracted_doi
            publisher = r.publisher or "Unknown"
            if publisher not in by_publisher:
                by_publisher[publisher] = []
            by_publisher[publisher].append(r.extracted_doi)

    return {
        'total_checked': len(results),
        'total_fabricated': len(fabricated),
        'fabrication_rate': len(fabricated) / len(results) if results else 0,
        'by_publisher': {k: len(v) for k, v in by_publisher.items()},
        'fabricated_dois': [r.extracted_doi for r in fabricated]
    }


def export_results(results: List[DOIValidationResult], output_path: str) -> None:
    """
    Export validation results to JSON.

    Args:
        results: List of DOIValidationResult objects
        output_path: Path for output JSON file
    """
    stats = {
        'total': len(results),
        'exists': sum(1 for r in results if r.status == DOIStatus.EXISTS),
        'fabricated': sum(1 for r in results if r.status == DOIStatus.FABRICATED),
        'not_doi': sum(1 for r in results if r.status == DOIStatus.NOT_DOI),
        'invalid_format': sum(1 for r in results if r.status == DOIStatus.INVALID_FORMAT),
        'api_error': sum(1 for r in results if r.status == DOIStatus.API_ERROR),
    }

    fabrication_analysis = analyze_fabrication_patterns(results)

    data = {
        'statistics': stats,
        'fabrication_analysis': fabrication_analysis,
        'results': [r.to_dict() for r in results]
    }

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


async def main():
    """Example usage of the DOI validator."""
    import argparse

    parser = argparse.ArgumentParser(description='Validate DOI existence (Phase 0)')
    parser.add_argument('input', help='Input JSON file from citation_extractor.py')
    parser.add_argument('-o', '--output', default='doi_validation.json', help='Output JSON file')
    parser.add_argument('-c', '--concurrency', type=int, default=5, help='Max concurrent requests')

    args = parser.parse_args()

    # Load citations
    with open(args.input, 'r', encoding='utf-8') as f:
        data = json.load(f)

    urls = [c['url'] for c in data['citations']]

    print(f"Validating {len(urls)} URLs for DOI existence...")

    validator = DOIValidator()

    def progress(completed, total):
        print(f"\rProgress: {completed}/{total}", end='', flush=True)

    results = await validator.validate_batch(urls, concurrency=args.concurrency, progress_callback=progress)

    print()  # New line after progress

    # Export results
    export_results(results, args.output)

    # Print summary
    exists_count = sum(1 for r in results if r.status == DOIStatus.EXISTS)
    fabricated_count = sum(1 for r in results if r.status == DOIStatus.FABRICATED)
    not_doi_count = sum(1 for r in results if r.status == DOIStatus.NOT_DOI)

    print(f"\nResults:")
    print(f"  DOIs exist: {exists_count}")
    print(f"  Fabricated DOIs: {fabricated_count}")
    print(f"  Not DOI URLs: {not_doi_count}")
    print(f"\nExported to: {args.output}")


if __name__ == '__main__':
    asyncio.run(main())
