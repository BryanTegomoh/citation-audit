#!/usr/bin/env python3
"""
Content Verifier Module (Phase 2)

Extracts content from URLs and compares against inline claims.

Part of the Four-Phase Citation Verification Pipeline.

NOTE: This module requires human judgment for final verification.
The automated components extract and flag potential mismatches
for human review.
"""

import re
import json
import asyncio
import aiohttp
from pathlib import Path
from dataclasses import dataclass, field, asdict
from typing import List, Optional, Dict, Tuple, Set
from bs4 import BeautifulSoup
from enum import Enum


class AlignmentStatus(Enum):
    """Content-claim alignment status."""
    ALIGNED = "aligned"
    PARTIAL_MATCH = "partial_match"
    MISMATCH = "mismatch"
    WRONG_PAPER = "wrong_paper"
    UNABLE_TO_VERIFY = "unable_to_verify"
    REQUIRES_REVIEW = "requires_review"


@dataclass
class ExtractedContent:
    """Content extracted from a URL."""
    url: str
    title: Optional[str] = None
    authors: Optional[List[str]] = None
    abstract: Optional[str] = None
    journal: Optional[str] = None
    year: Optional[str] = None
    doi: Optional[str] = None
    keywords: Optional[List[str]] = None
    full_text_available: bool = False
    extraction_method: str = "html"
    raw_text: Optional[str] = None

    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class ClaimAnalysis:
    """Analysis of an inline claim."""
    raw_text: str
    claim_type: str  # "statistic", "finding", "conclusion", "attribution"
    statistics: List[Dict[str, str]] = field(default_factory=list)
    key_terms: List[str] = field(default_factory=list)
    expected_topic: Optional[str] = None

    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class ContentVerificationResult:
    """Result of content verification."""
    url: str
    inline_claim: str
    extracted_content: Optional[ExtractedContent]
    claim_analysis: Optional[ClaimAnalysis]
    alignment_status: AlignmentStatus
    confidence: float  # 0.0 to 1.0
    mismatches: List[str] = field(default_factory=list)
    notes: str = ""

    def to_dict(self) -> Dict:
        result = asdict(self)
        result['alignment_status'] = self.alignment_status.value
        if self.extracted_content:
            result['extracted_content'] = self.extracted_content.to_dict()
        if self.claim_analysis:
            result['claim_analysis'] = self.claim_analysis.to_dict()
        return result


class ContentExtractor:
    """
    Extracts structured content from academic paper URLs.
    """

    # Patterns for metadata extraction
    TITLE_PATTERNS = [
        (r'<h1[^>]*class="[^"]*article-title[^"]*"[^>]*>([^<]+)</h1>', 'article-title'),
        (r'<title[^>]*>([^<]+)</title>', 'html-title'),
        (r'<meta[^>]*name="citation_title"[^>]*content="([^"]+)"', 'meta-citation'),
        (r'<meta[^>]*property="og:title"[^>]*content="([^"]+)"', 'og-title'),
    ]

    AUTHOR_PATTERNS = [
        (r'<meta[^>]*name="citation_author"[^>]*content="([^"]+)"', 'meta-citation'),
        (r'<meta[^>]*name="DC.Creator"[^>]*content="([^"]+)"', 'dc-creator'),
    ]

    ABSTRACT_PATTERNS = [
        (r'<section[^>]*class="[^"]*abstract[^"]*"[^>]*>(.*?)</section>', 'section'),
        (r'<div[^>]*class="[^"]*abstract[^"]*"[^>]*>(.*?)</div>', 'div'),
        (r'<meta[^>]*name="citation_abstract"[^>]*content="([^"]+)"', 'meta'),
        (r'<meta[^>]*name="DC.Description"[^>]*content="([^"]+)"', 'dc'),
    ]

    USER_AGENT = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )

    def __init__(self, timeout: int = 30):
        self.timeout = timeout

    async def extract(self, url: str) -> ExtractedContent:
        """
        Extract content from a URL.

        Args:
            url: URL to extract from

        Returns:
            ExtractedContent with extracted metadata
        """
        content = ExtractedContent(url=url)

        headers = {'User-Agent': self.USER_AGENT}
        timeout_config = aiohttp.ClientTimeout(total=self.timeout)

        try:
            async with aiohttp.ClientSession(
                timeout=timeout_config,
                headers=headers
            ) as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        html = await response.text()
                        content = self._extract_from_html(url, html)
        except Exception as e:
            content.raw_text = f"Error extracting: {str(e)}"

        return content

    def _extract_from_html(self, url: str, html: str) -> ExtractedContent:
        """Extract metadata from HTML content."""
        content = ExtractedContent(url=url, extraction_method="html")

        # Use BeautifulSoup for robust parsing
        soup = BeautifulSoup(html, 'html.parser')

        # Extract title
        for pattern, method in self.TITLE_PATTERNS:
            match = re.search(pattern, html, re.IGNORECASE | re.DOTALL)
            if match:
                content.title = self._clean_text(match.group(1))
                break

        if not content.title:
            title_tag = soup.find('title')
            if title_tag:
                content.title = self._clean_text(title_tag.get_text())

        # Extract authors
        authors = []
        for pattern, method in self.AUTHOR_PATTERNS:
            for match in re.finditer(pattern, html, re.IGNORECASE):
                authors.append(self._clean_text(match.group(1)))
        content.authors = authors if authors else None

        # Extract abstract
        for pattern, method in self.ABSTRACT_PATTERNS:
            match = re.search(pattern, html, re.IGNORECASE | re.DOTALL)
            if match:
                abstract_html = match.group(1)
                abstract_soup = BeautifulSoup(abstract_html, 'html.parser')
                content.abstract = self._clean_text(abstract_soup.get_text())
                break

        # Extract journal
        journal_meta = soup.find('meta', attrs={'name': 'citation_journal_title'})
        if journal_meta:
            content.journal = journal_meta.get('content')

        # Extract year
        date_meta = soup.find('meta', attrs={'name': 'citation_publication_date'})
        if date_meta:
            date_str = date_meta.get('content', '')
            year_match = re.search(r'(19|20)\d{2}', date_str)
            if year_match:
                content.year = year_match.group(0)

        # Extract DOI
        doi_meta = soup.find('meta', attrs={'name': 'citation_doi'})
        if doi_meta:
            content.doi = doi_meta.get('content')

        # Extract main text for keyword analysis
        main_content = soup.find('main') or soup.find('article') or soup.find('body')
        if main_content:
            content.raw_text = self._clean_text(main_content.get_text())[:5000]

        return content

    def _clean_text(self, text: str) -> str:
        """Clean extracted text."""
        if not text:
            return ""
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        # Remove HTML entities
        text = re.sub(r'&[a-z]+;', ' ', text)
        return text.strip()


class ClaimAnalyzer:
    """
    Analyzes inline claims to identify what needs to be verified.
    """

    # Patterns for different claim types
    STATISTIC_PATTERNS = [
        (r'(\d+(?:\.\d+)?)\s*%', 'percentage'),
        (r'p\s*[<>=]\s*(\d+(?:\.\d+)?)', 'p_value'),
        (r'(\d+(?:,\d+)*)\s*(?:patients?|participants?|subjects?)', 'sample_size'),
        (r'AUC\s*(?:of\s*)?(\d+(?:\.\d+)?)', 'auc'),
        (r'sensitivity\s*(?:of\s*)?(\d+(?:\.\d+)?)\s*%', 'sensitivity'),
        (r'specificity\s*(?:of\s*)?(\d+(?:\.\d+)?)\s*%', 'specificity'),
        (r'PPV\s*(?:of\s*)?(\d+(?:\.\d+)?)\s*%', 'ppv'),
        (r'NPV\s*(?:of\s*)?(\d+(?:\.\d+)?)\s*%', 'npv'),
    ]

    FINDING_INDICATORS = [
        'showed', 'demonstrated', 'found', 'revealed', 'reported',
        'achieved', 'resulted', 'indicated', 'suggested', 'confirmed'
    ]

    CONCLUSION_INDICATORS = [
        'therefore', 'thus', 'indicating', 'suggesting', 'confirming',
        'supporting', 'concluding', 'implying'
    ]

    def analyze(self, claim_text: str) -> ClaimAnalysis:
        """
        Analyze an inline claim.

        Args:
            claim_text: The surrounding text of a citation

        Returns:
            ClaimAnalysis with identified claim components
        """
        analysis = ClaimAnalysis(raw_text=claim_text, claim_type="unknown")

        # Extract statistics
        for pattern, stat_type in self.STATISTIC_PATTERNS:
            for match in re.finditer(pattern, claim_text, re.IGNORECASE):
                analysis.statistics.append({
                    'type': stat_type,
                    'value': match.group(1),
                    'context': claim_text[max(0, match.start()-20):match.end()+20]
                })

        # Identify claim type
        claim_lower = claim_text.lower()

        if analysis.statistics:
            analysis.claim_type = "statistic"
        elif any(ind in claim_lower for ind in self.FINDING_INDICATORS):
            analysis.claim_type = "finding"
        elif any(ind in claim_lower for ind in self.CONCLUSION_INDICATORS):
            analysis.claim_type = "conclusion"
        else:
            analysis.claim_type = "attribution"

        # Extract key terms (nouns and medical terms)
        # Simple extraction: words longer than 4 chars, capitalized, or medical-looking
        words = re.findall(r'\b([A-Za-z]{4,})\b', claim_text)
        key_terms = []
        for word in words:
            # Skip common words
            if word.lower() in {'that', 'this', 'with', 'from', 'have', 'were', 'been', 'their'}:
                continue
            key_terms.append(word.lower())
        analysis.key_terms = list(set(key_terms))[:10]

        return analysis


class ContentAlignmentChecker:
    """
    Checks alignment between extracted content and inline claims.
    """

    def check_alignment(
        self,
        content: ExtractedContent,
        claim: ClaimAnalysis
    ) -> Tuple[AlignmentStatus, float, List[str]]:
        """
        Check if extracted content aligns with the claim.

        Args:
            content: Extracted paper content
            claim: Analyzed inline claim

        Returns:
            Tuple of (status, confidence, mismatches)
        """
        mismatches = []
        confidence = 0.5  # Default moderate confidence

        # Check for topic alignment
        topic_aligned = self._check_topic_alignment(content, claim)
        if not topic_aligned:
            return AlignmentStatus.WRONG_PAPER, 0.8, ["Topic does not match claim"]

        # Check statistics if present
        if claim.statistics:
            stat_aligned, stat_mismatches = self._check_statistics(content, claim)
            mismatches.extend(stat_mismatches)
            if not stat_aligned and stat_mismatches:
                return AlignmentStatus.MISMATCH, 0.7, mismatches

        # If we have good topic match and no stat mismatches
        if topic_aligned and not mismatches:
            return AlignmentStatus.ALIGNED, 0.6, []

        # Partial match if topic aligned but some issues
        if topic_aligned and mismatches:
            return AlignmentStatus.PARTIAL_MATCH, 0.5, mismatches

        return AlignmentStatus.REQUIRES_REVIEW, 0.3, mismatches

    def _check_topic_alignment(self, content: ExtractedContent, claim: ClaimAnalysis) -> bool:
        """Check if paper topic aligns with claim topic."""
        if not content.title and not content.abstract:
            return True  # Can't verify, assume aligned

        # Combine content text
        content_text = ' '.join(filter(None, [
            content.title,
            content.abstract,
            content.raw_text
        ])).lower()

        # Check if key terms from claim appear in content
        if not claim.key_terms:
            return True

        matches = sum(1 for term in claim.key_terms if term in content_text)
        match_ratio = matches / len(claim.key_terms) if claim.key_terms else 1

        return match_ratio >= 0.3  # At least 30% of key terms should match

    def _check_statistics(
        self,
        content: ExtractedContent,
        claim: ClaimAnalysis
    ) -> Tuple[bool, List[str]]:
        """Check if claimed statistics appear in content."""
        mismatches = []

        content_text = ' '.join(filter(None, [
            content.abstract,
            content.raw_text
        ])) if content else ""

        for stat in claim.statistics:
            stat_value = stat['value']
            stat_type = stat['type']

            # Look for the statistic in content
            if stat_value not in content_text:
                mismatches.append(
                    f"{stat_type} value {stat_value} not found in paper content"
                )

        all_aligned = len(mismatches) == 0
        return all_aligned, mismatches


class ContentVerifier:
    """
    Main content verification class.

    Usage:
        verifier = ContentVerifier()
        result = await verifier.verify(url, inline_claim)
    """

    def __init__(self):
        self.extractor = ContentExtractor()
        self.claim_analyzer = ClaimAnalyzer()
        self.alignment_checker = ContentAlignmentChecker()

    async def verify(self, url: str, inline_claim: str) -> ContentVerificationResult:
        """
        Verify content alignment for a citation.

        Args:
            url: Citation URL
            inline_claim: Surrounding text from source document

        Returns:
            ContentVerificationResult
        """
        # Extract content from URL
        content = await self.extractor.extract(url)

        # Analyze the inline claim
        claim_analysis = self.claim_analyzer.analyze(inline_claim)

        # Check alignment
        if content.title or content.abstract:
            status, confidence, mismatches = self.alignment_checker.check_alignment(
                content, claim_analysis
            )
        else:
            status = AlignmentStatus.UNABLE_TO_VERIFY
            confidence = 0.0
            mismatches = ["Could not extract content from URL"]

        return ContentVerificationResult(
            url=url,
            inline_claim=inline_claim,
            extracted_content=content,
            claim_analysis=claim_analysis,
            alignment_status=status,
            confidence=confidence,
            mismatches=mismatches,
            notes="Automated analysis - requires human review for confirmation"
        )

    async def verify_batch(
        self,
        citations: List[Dict],
        concurrency: int = 5
    ) -> List[ContentVerificationResult]:
        """
        Verify multiple citations.

        Args:
            citations: List of dicts with 'url' and 'surrounding_text' keys
            concurrency: Max concurrent verifications

        Returns:
            List of ContentVerificationResult
        """
        semaphore = asyncio.Semaphore(concurrency)

        async def verify_with_limit(citation: Dict) -> ContentVerificationResult:
            async with semaphore:
                return await self.verify(
                    citation['url'],
                    citation.get('surrounding_text', '')
                )

        tasks = [verify_with_limit(c) for c in citations]
        return await asyncio.gather(*tasks)


def export_results(results: List[ContentVerificationResult], output_path: str) -> None:
    """Export verification results to JSON."""
    stats = {
        'total': len(results),
        'aligned': sum(1 for r in results if r.alignment_status == AlignmentStatus.ALIGNED),
        'partial': sum(1 for r in results if r.alignment_status == AlignmentStatus.PARTIAL_MATCH),
        'mismatch': sum(1 for r in results if r.alignment_status == AlignmentStatus.MISMATCH),
        'wrong_paper': sum(1 for r in results if r.alignment_status == AlignmentStatus.WRONG_PAPER),
        'unable_to_verify': sum(1 for r in results if r.alignment_status == AlignmentStatus.UNABLE_TO_VERIFY),
        'requires_review': sum(1 for r in results if r.alignment_status == AlignmentStatus.REQUIRES_REVIEW),
    }

    data = {
        'statistics': stats,
        'note': 'These are automated results requiring human verification',
        'results': [r.to_dict() for r in results]
    }

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


async def main():
    """Example usage."""
    import argparse

    parser = argparse.ArgumentParser(description='Verify content alignment for citations')
    parser.add_argument('input', help='Input JSON file from citation_extractor.py')
    parser.add_argument('-o', '--output', default='content_verification.json', help='Output JSON file')
    parser.add_argument('-c', '--concurrency', type=int, default=5, help='Max concurrent requests')

    args = parser.parse_args()

    with open(args.input, 'r', encoding='utf-8') as f:
        data = json.load(f)

    citations = data['citations']
    print(f"Verifying content alignment for {len(citations)} citations...")

    verifier = ContentVerifier()
    results = await verifier.verify_batch(citations, concurrency=args.concurrency)

    export_results(results, args.output)

    # Print summary
    aligned = sum(1 for r in results if r.alignment_status == AlignmentStatus.ALIGNED)
    mismatched = sum(1 for r in results if r.alignment_status in [
        AlignmentStatus.MISMATCH, AlignmentStatus.WRONG_PAPER
    ])

    print(f"\nResults:")
    print(f"  Aligned: {aligned}")
    print(f"  Mismatched/Wrong: {mismatched}")
    print(f"  Requires review: {len(results) - aligned - mismatched}")
    print(f"\nExported to: {args.output}")


if __name__ == '__main__':
    asyncio.run(main())
