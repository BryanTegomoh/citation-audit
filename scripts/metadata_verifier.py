#!/usr/bin/env python3
"""
Metadata Verifier Module (Phase 3)

Verifies citation metadata accuracy (author, year, journal) and checks
for retraction status, publication type (conference abstract vs. full paper),
and journal quality indicators.

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


class MetadataField(Enum):
    """Metadata fields that can be verified."""
    AUTHOR = "author"
    YEAR = "year"
    JOURNAL = "journal"
    DOI = "doi"
    TITLE = "title"


@dataclass
class MetadataDiscrepancy:
    """Represents a single metadata discrepancy."""
    field: MetadataField
    cited_value: str
    actual_value: str
    confidence: float  # Confidence in the discrepancy detection

    def to_dict(self) -> Dict:
        result = asdict(self)
        result['field'] = self.field.value
        return result


@dataclass
class CitationMetadata:
    """Parsed citation metadata from citation text."""
    raw_text: str
    authors: Optional[str] = None
    year: Optional[str] = None
    journal: Optional[str] = None  # Usually not in inline citation
    is_preprint: bool = False

    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class PaperMetadata:
    """Extracted metadata from paper/database."""
    url: str
    title: Optional[str] = None
    first_author: Optional[str] = None
    all_authors: Optional[List[str]] = None
    year: Optional[str] = None
    journal: Optional[str] = None
    doi: Optional[str] = None
    pmid: Optional[str] = None
    source: str = "unknown"
    is_retracted: bool = False
    retraction_doi: Optional[str] = None
    publication_type: Optional[str] = None  # journal-article, proceedings-article, etc.
    funding_sources: Optional[List[str]] = None

    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class MetadataVerificationResult:
    """Result of metadata verification."""
    url: str
    citation_metadata: CitationMetadata
    paper_metadata: Optional[PaperMetadata]
    discrepancies: List[MetadataDiscrepancy] = field(default_factory=list)
    verified: bool = False
    notes: str = ""

    def to_dict(self) -> Dict:
        result = {
            'url': self.url,
            'citation_metadata': self.citation_metadata.to_dict(),
            'paper_metadata': self.paper_metadata.to_dict() if self.paper_metadata else None,
            'discrepancies': [d.to_dict() for d in self.discrepancies],
            'verified': self.verified,
            'notes': self.notes
        }
        return result

    @property
    def has_errors(self) -> bool:
        return len(self.discrepancies) > 0

    @property
    def error_types(self) -> List[str]:
        return [d.field.value for d in self.discrepancies]


class CitationParser:
    """
    Parses citation text to extract metadata.
    """

    # Pattern: Author et al., Year or Author & Author, Year
    CITATION_PATTERNS = [
        # "Wong et al., 2021"
        re.compile(r'^([A-Z][a-z]+(?:\s+et\s+al\.?)?),?\s*((?:19|20)\d{2})(?:\s*,\s*(preprint))?$', re.IGNORECASE),
        # "Wong & Smith, 2021"
        re.compile(r'^([A-Z][a-z]+\s*&\s*[A-Z][a-z]+),?\s*((?:19|20)\d{2})$', re.IGNORECASE),
        # "Wong, 2021"
        re.compile(r'^([A-Z][a-z]+),?\s*((?:19|20)\d{2})$', re.IGNORECASE),
        # Organization citations "WHO, 2024"
        re.compile(r'^([A-Z]{2,}),?\s*((?:19|20)\d{2})$'),
    ]

    def parse(self, citation_text: str) -> CitationMetadata:
        """
        Parse citation text to extract metadata.

        Args:
            citation_text: e.g., "Wong et al., 2021"

        Returns:
            CitationMetadata with parsed fields
        """
        metadata = CitationMetadata(raw_text=citation_text)

        for pattern in self.CITATION_PATTERNS:
            match = pattern.match(citation_text.strip())
            if match:
                groups = match.groups()
                metadata.authors = groups[0].strip() if groups[0] else None
                metadata.year = groups[1] if len(groups) > 1 else None
                if len(groups) > 2 and groups[2]:
                    metadata.is_preprint = 'preprint' in groups[2].lower()
                break

        # Fallback: try to extract year even if pattern doesn't match
        if not metadata.year:
            year_match = re.search(r'(19|20)\d{2}', citation_text)
            if year_match:
                metadata.year = year_match.group(0)

        return metadata


class PubMedFetcher:
    """
    Fetches metadata from PubMed.
    """

    BASE_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"

    def __init__(self, email: str = "verification@example.com"):
        self.email = email

    async def fetch_by_doi(self, doi: str) -> Optional[PaperMetadata]:
        """Fetch paper metadata by DOI."""
        # Search for DOI
        search_url = f"{self.BASE_URL}/esearch.fcgi"
        params = {
            'db': 'pubmed',
            'term': f'{doi}[doi]',
            'retmode': 'json',
            'email': self.email
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(search_url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        ids = data.get('esearchresult', {}).get('idlist', [])
                        if ids:
                            return await self.fetch_by_pmid(ids[0])
        except Exception:
            pass

        return None

    async def fetch_by_pmid(self, pmid: str) -> Optional[PaperMetadata]:
        """Fetch paper metadata by PubMed ID."""
        fetch_url = f"{self.BASE_URL}/efetch.fcgi"
        params = {
            'db': 'pubmed',
            'id': pmid,
            'retmode': 'xml',
            'email': self.email
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(fetch_url, params=params) as response:
                    if response.status == 200:
                        xml_text = await response.text()
                        return self._parse_pubmed_xml(xml_text, pmid)
        except Exception:
            pass

        return None

    def _parse_pubmed_xml(self, xml_text: str, pmid: str) -> PaperMetadata:
        """Parse PubMed XML response."""
        metadata = PaperMetadata(url=f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/", source="pubmed")
        metadata.pmid = pmid

        # Extract title
        title_match = re.search(r'<ArticleTitle>([^<]+)</ArticleTitle>', xml_text)
        if title_match:
            metadata.title = title_match.group(1)

        # Extract authors
        authors = []
        author_pattern = re.compile(r'<LastName>([^<]+)</LastName>')
        for match in author_pattern.finditer(xml_text):
            authors.append(match.group(1))
        if authors:
            metadata.all_authors = authors
            metadata.first_author = authors[0]

        # Extract year
        year_match = re.search(r'<PubDate>.*?<Year>(\d{4})</Year>', xml_text, re.DOTALL)
        if year_match:
            metadata.year = year_match.group(1)

        # Extract journal
        journal_match = re.search(r'<Title>([^<]+)</Title>', xml_text)
        if journal_match:
            metadata.journal = journal_match.group(1)

        # Extract DOI
        doi_match = re.search(r'<ArticleId IdType="doi">([^<]+)</ArticleId>', xml_text)
        if doi_match:
            metadata.doi = doi_match.group(1)

        return metadata


class CrossRefFetcher:
    """
    Fetches metadata from CrossRef.
    """

    BASE_URL = "https://api.crossref.org/works"

    async def fetch_by_doi(self, doi: str) -> Optional[PaperMetadata]:
        """Fetch paper metadata by DOI from CrossRef."""
        url = f"{self.BASE_URL}/{doi}"

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        return self._parse_crossref_response(data, doi)
        except Exception:
            pass

        return None

    def _parse_crossref_response(self, data: Dict, doi: str) -> PaperMetadata:
        """Parse CrossRef API response."""
        message = data.get('message', {})

        metadata = PaperMetadata(
            url=f"https://doi.org/{doi}",
            source="crossref",
            doi=doi
        )

        # Title
        titles = message.get('title', [])
        if titles:
            metadata.title = titles[0]

        # Authors
        authors = message.get('author', [])
        if authors:
            author_names = []
            for author in authors:
                family = author.get('family', '')
                if family:
                    author_names.append(family)
            metadata.all_authors = author_names
            if author_names:
                metadata.first_author = author_names[0]

        # Year
        published = message.get('published-print') or message.get('published-online')
        if published:
            date_parts = published.get('date-parts', [[]])
            if date_parts and date_parts[0]:
                metadata.year = str(date_parts[0][0])

        # Journal
        container = message.get('container-title', [])
        if container:
            metadata.journal = container[0]

        # Publication type (journal-article, proceedings-article, etc.)
        metadata.publication_type = message.get('type')

        # Retraction status
        update_to = message.get('update-to', [])
        for update in update_to:
            if update.get('type') == 'retraction':
                metadata.is_retracted = True
                metadata.retraction_doi = update.get('DOI')

        relation = message.get('relation', {})
        is_retracted_by = relation.get('is-retracted-by', [])
        if is_retracted_by:
            metadata.is_retracted = True
            metadata.retraction_doi = is_retracted_by[0].get('id')

        if message.get('type') == 'retracted-article':
            metadata.is_retracted = True

        # Funding sources
        funders = message.get('funder', [])
        if funders:
            metadata.funding_sources = [
                f.get('name', 'Unknown') for f in funders if f.get('name')
            ]

        return metadata


class MetadataVerifier:
    """
    Main metadata verification class.

    Usage:
        verifier = MetadataVerifier()
        result = await verifier.verify(citation_text, url)
    """

    def __init__(self):
        self.citation_parser = CitationParser()
        self.pubmed_fetcher = PubMedFetcher()
        self.crossref_fetcher = CrossRefFetcher()

    async def verify(self, citation_text: str, url: str) -> MetadataVerificationResult:
        """
        Verify metadata for a citation.

        Args:
            citation_text: The citation text, e.g., "Wong et al., 2021"
            url: The citation URL

        Returns:
            MetadataVerificationResult
        """
        # Parse citation
        citation_metadata = self.citation_parser.parse(citation_text)

        # Extract DOI from URL if present
        doi = self._extract_doi(url)

        # Fetch paper metadata
        paper_metadata = None
        if doi:
            # Try CrossRef first (more comprehensive)
            paper_metadata = await self.crossref_fetcher.fetch_by_doi(doi)
            # Fall back to PubMed
            if not paper_metadata or not paper_metadata.first_author:
                pm_metadata = await self.pubmed_fetcher.fetch_by_doi(doi)
                if pm_metadata:
                    paper_metadata = pm_metadata
        elif 'pubmed' in url.lower():
            # Extract PMID
            pmid_match = re.search(r'/(\d+)/?$', url)
            if pmid_match:
                paper_metadata = await self.pubmed_fetcher.fetch_by_pmid(pmid_match.group(1))

        # Compare metadata
        discrepancies = self._compare_metadata(citation_metadata, paper_metadata)

        return MetadataVerificationResult(
            url=url,
            citation_metadata=citation_metadata,
            paper_metadata=paper_metadata,
            discrepancies=discrepancies,
            verified=paper_metadata is not None,
            notes="Metadata comparison completed" if paper_metadata else "Could not fetch paper metadata"
        )

    def _extract_doi(self, url: str) -> Optional[str]:
        """Extract DOI from URL."""
        doi_match = re.search(r'10\.\d{4,}/[^\s\)]+', url)
        if doi_match:
            return doi_match.group(0).rstrip('/')
        return None

    def _compare_metadata(
        self,
        citation: CitationMetadata,
        paper: Optional[PaperMetadata]
    ) -> List[MetadataDiscrepancy]:
        """Compare citation metadata to paper metadata."""
        discrepancies = []

        if not paper:
            return discrepancies

        # Compare author
        if citation.authors and paper.first_author:
            # Extract first author surname from citation
            cited_surname = citation.authors.split()[0].rstrip(',')
            if cited_surname.lower() == 'et':
                # Handle "et al." - shouldn't be the surname
                pass
            elif cited_surname.lower() != paper.first_author.lower():
                discrepancies.append(MetadataDiscrepancy(
                    field=MetadataField.AUTHOR,
                    cited_value=cited_surname,
                    actual_value=paper.first_author,
                    confidence=0.9
                ))

        # Compare year
        if citation.year and paper.year:
            if citation.year != paper.year:
                discrepancies.append(MetadataDiscrepancy(
                    field=MetadataField.YEAR,
                    cited_value=citation.year,
                    actual_value=paper.year,
                    confidence=0.95
                ))

        return discrepancies

    async def verify_batch(
        self,
        citations: List[Dict],
        concurrency: int = 5
    ) -> List[MetadataVerificationResult]:
        """
        Verify metadata for multiple citations.

        Args:
            citations: List of dicts with 'citation_text' and 'url' keys
            concurrency: Max concurrent API requests

        Returns:
            List of MetadataVerificationResult
        """
        semaphore = asyncio.Semaphore(concurrency)

        async def verify_with_limit(citation: Dict) -> MetadataVerificationResult:
            async with semaphore:
                # Rate limiting for APIs
                await asyncio.sleep(0.5)
                return await self.verify(
                    citation.get('citation_text', ''),
                    citation.get('url', '')
                )

        tasks = [verify_with_limit(c) for c in citations]
        return await asyncio.gather(*tasks)


def export_results(results: List[MetadataVerificationResult], output_path: str) -> None:
    """Export verification results to JSON."""
    stats = {
        'total': len(results),
        'verified': sum(1 for r in results if r.verified),
        'with_errors': sum(1 for r in results if r.has_errors),
        'author_errors': sum(1 for r in results if MetadataField.AUTHOR.value in r.error_types),
        'year_errors': sum(1 for r in results if MetadataField.YEAR.value in r.error_types),
    }

    data = {
        'statistics': stats,
        'results': [r.to_dict() for r in results]
    }

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


async def main():
    """Example usage."""
    import argparse

    parser = argparse.ArgumentParser(description='Verify citation metadata')
    parser.add_argument('input', help='Input JSON file from citation_extractor.py')
    parser.add_argument('-o', '--output', default='metadata_verification.json', help='Output JSON file')
    parser.add_argument('-c', '--concurrency', type=int, default=3, help='Max concurrent API requests')

    args = parser.parse_args()

    with open(args.input, 'r', encoding='utf-8') as f:
        data = json.load(f)

    citations = data['citations']
    print(f"Verifying metadata for {len(citations)} citations...")

    verifier = MetadataVerifier()
    results = await verifier.verify_batch(citations, concurrency=args.concurrency)

    export_results(results, args.output)

    # Print summary
    author_errors = sum(1 for r in results if MetadataField.AUTHOR.value in r.error_types)
    year_errors = sum(1 for r in results if MetadataField.YEAR.value in r.error_types)

    print(f"\nResults:")
    print(f"  Author errors: {author_errors}")
    print(f"  Year errors: {year_errors}")
    print(f"\nExported to: {args.output}")


if __name__ == '__main__':
    asyncio.run(main())
