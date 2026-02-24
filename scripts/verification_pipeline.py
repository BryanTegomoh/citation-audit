#!/usr/bin/env python3
"""
Citation Verification Pipeline

A domain-agnostic tool for verifying academic citations in any text document.
This pipeline systematically validates citations through five phases, detecting
errors ranging from broken URLs to fabricated references.

Part of the Five-Phase Citation Verification Pipeline.
See METHODOLOGY.md for complete documentation.

Phases:
  0: DOI Existence Validation - Check if DOI exists in CrossRef registry
  1: URL Resolution Testing - Check if URL resolves (HTTP status)
  2: Content-Claim Alignment - Verify paper supports the claim made
  3: Metadata Accuracy - Verify author, year, journal are correct
  4: Correction Analysis - Identify fixes needed (analysis only)

Usage:
    # Verify all markdown files in a directory
    python verification_pipeline.py ./content/ -o report.json

    # Verify with markdown report
    python verification_pipeline.py ./content/ -o report.json --markdown

    # Run specific phases only
    python verification_pipeline.py ./content/ --phases 0 1

Supported file types: .md, .qmd, .rst, .txt (with markdown citations)
"""

import argparse
import asyncio
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional
from dataclasses import dataclass, field, asdict
from enum import Enum

# Import pipeline components
from citation_extractor import CitationExtractor, Citation, export_citations
from doi_validator import DOIValidator, DOIStatus, DOIValidationResult
from url_verifier import URLVerifier, URLStatus, URLVerificationResult
from content_verifier import ContentVerifier, AlignmentStatus, ContentVerificationResult
from metadata_verifier import MetadataVerifier, MetadataVerificationResult, MetadataField


class ErrorCategory(Enum):
    """Standardized error categories for the final report."""
    BROKEN_URL = "broken_url"
    FABRICATED_DOI = "fabricated_doi"  # NEW: DOI format valid but doesn't exist
    WRONG_PAPER = "wrong_paper"
    AUTHOR_ERROR = "author_error"
    YEAR_ERROR = "year_error"
    JOURNAL_ERROR = "journal_error"
    CLAIM_MISMATCH = "claim_mismatch"
    METRIC_ERROR = "metric_error"
    FABRICATED_STATISTIC = "fabricated_statistic"  # NEW: Specific number without source
    INVERTED_STATISTICS = "inverted_statistics"  # Correct numbers assigned to wrong metric labels
    FABRICATED_REPOSITORY = "fabricated_repository"  # GitHub/GitLab URL returns 404 for non-existent repo
    GENERIC_URL = "generic_url"  # URL resolves to homepage, not specific cited document
    CHIMERA_CITATION = "chimera_citation"  # Real author/stats from Paper A in fabricated Paper B
    FABRICATED = "fabricated"
    VERIFIED_CORRECT = "verified_correct"
    UNABLE_TO_VERIFY = "unable_to_verify"


@dataclass
class VerificationResult:
    """Comprehensive verification result for a single citation."""
    # Citation info
    citation_text: str
    url: str
    file_path: str
    line_number: int
    surrounding_text: str

    # Phase results
    doi_result: Optional[DOIValidationResult] = None  # Phase 0 (NEW)
    url_result: Optional[URLVerificationResult] = None  # Phase 1
    content_result: Optional[ContentVerificationResult] = None  # Phase 2
    metadata_result: Optional[MetadataVerificationResult] = None  # Phase 3

    # Claim analysis (for fabricated statistic detection)
    has_specific_statistic: bool = False
    claimed_statistics: List[str] = field(default_factory=list)

    # Final assessment
    error_category: ErrorCategory = ErrorCategory.UNABLE_TO_VERIFY
    errors: List[str] = field(default_factory=list)
    needs_correction: bool = False
    suggested_correction: Optional[str] = None
    confidence: float = 0.0

    def to_dict(self) -> Dict:
        return {
            'citation_text': self.citation_text,
            'url': self.url,
            'file_path': self.file_path,
            'line_number': self.line_number,
            'surrounding_text': self.surrounding_text,
            'doi_result': self.doi_result.to_dict() if self.doi_result else None,
            'url_result': self.url_result.to_dict() if self.url_result else None,
            'content_result': self.content_result.to_dict() if self.content_result else None,
            'metadata_result': self.metadata_result.to_dict() if self.metadata_result else None,
            'has_specific_statistic': self.has_specific_statistic,
            'claimed_statistics': self.claimed_statistics,
            'error_category': self.error_category.value,
            'errors': self.errors,
            'needs_correction': self.needs_correction,
            'suggested_correction': self.suggested_correction,
            'confidence': self.confidence
        }


@dataclass
class PipelineReport:
    """Complete pipeline report."""
    timestamp: str
    source_path: str
    total_citations: int
    unique_citations: int
    duplicate_citations: int
    results: List[VerificationResult]

    # Summary statistics
    verified_correct: int = 0
    total_errors: int = 0
    broken_urls: int = 0
    fabricated_dois: int = 0  # NEW
    wrong_papers: int = 0
    author_errors: int = 0
    year_errors: int = 0
    claim_mismatches: int = 0
    fabricated_statistics: int = 0  # NEW
    unable_to_verify: int = 0

    def to_dict(self) -> Dict:
        return {
            'timestamp': self.timestamp,
            'source_path': self.source_path,
            'summary': {
                'total_citations': self.total_citations,
                'unique_citations': self.unique_citations,
                'duplicate_citations': self.duplicate_citations,
                'verified_correct': self.verified_correct,
                'total_errors': self.total_errors,
                'error_rate': f"{(self.total_errors / self.unique_citations * 100):.1f}%" if self.unique_citations > 0 else "N/A",
                'by_category': {
                    'broken_urls': self.broken_urls,
                    'fabricated_dois': self.fabricated_dois,
                    'wrong_papers': self.wrong_papers,
                    'author_errors': self.author_errors,
                    'year_errors': self.year_errors,
                    'claim_mismatches': self.claim_mismatches,
                    'fabricated_statistics': self.fabricated_statistics,
                    'unable_to_verify': self.unable_to_verify
                }
            },
            'results': [r.to_dict() for r in self.results]
        }


class VerificationPipeline:
    """
    Main verification pipeline orchestrator.

    Runs five phases:
      Phase 0: DOI existence validation
      Phase 1: URL resolution testing
      Phase 2: Content-claim alignment
      Phase 3: Metadata accuracy
      Phase 4: Correction (analysis only)

    Usage:
        pipeline = VerificationPipeline()
        report = await pipeline.run("./content/")
    """

    # Patterns for detecting specific statistics in claims
    STATISTIC_PATTERNS = [
        r'(\d+(?:\.\d+)?)\s*%',  # percentages
        r'p\s*[<>=]\s*(\d+(?:\.\d+)?)',  # p-values
        r'(\d+(?:,\d+)*)\s*(?:patients?|participants?|subjects?)',  # sample sizes
        r'AUC\s*(?:of\s*)?(\d+(?:\.\d+)?)',  # AUC values
        r'sensitivity\s*(?:of\s*)?(\d+(?:\.\d+)?)',  # sensitivity
        r'specificity\s*(?:of\s*)?(\d+(?:\.\d+)?)',  # specificity
    ]

    def __init__(
        self,
        doi_concurrency: int = 5,
        url_concurrency: int = 10,
        content_concurrency: int = 5,
        metadata_concurrency: int = 3
    ):
        self.extractor = CitationExtractor()
        self.doi_validator = DOIValidator()  # Phase 0
        self.url_verifier = URLVerifier()
        self.content_verifier = ContentVerifier()
        self.metadata_verifier = MetadataVerifier()

        self.doi_concurrency = doi_concurrency
        self.url_concurrency = url_concurrency
        self.content_concurrency = content_concurrency
        self.metadata_concurrency = metadata_concurrency

    def _extract_statistics(self, text: str) -> List[str]:
        """Extract specific statistics from claim text."""
        import re
        statistics = []
        for pattern in self.STATISTIC_PATTERNS:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                statistics.append(match.group(0))
        return statistics

    async def run(
        self,
        source_path: str,
        file_pattern: str = "*.qmd",
        recursive: bool = True,
        phases: List[int] = [0, 1, 2, 3]
    ) -> PipelineReport:
        """
        Run the complete verification pipeline.

        Args:
            source_path: Path to file or directory
            file_pattern: Glob pattern for files
            recursive: Search subdirectories
            phases: Which phases to run (0=DOI, 1=URL, 2=Content, 3=Metadata)

        Returns:
            PipelineReport with all results
        """
        print(f"Starting verification pipeline for: {source_path}")
        print(f"Phases to run: {phases}")
        print("-" * 50)

        # Extraction: Extract citations
        print("\n[Extraction] Extracting citations...")
        path = Path(source_path)
        if path.is_file():
            all_citations = self.extractor.extract_from_file(path)
        else:
            all_citations = self.extractor.extract_from_directory(
                path, pattern=file_pattern, recursive=recursive
            )

        unique_citations, duplicates = self.extractor.deduplicate(all_citations)

        print(f"  Total citations: {len(all_citations)}")
        print(f"  Unique citations: {len(unique_citations)}")
        print(f"  Duplicates: {len(duplicates)}")

        # Initialize results with statistic extraction
        results = []
        for citation in unique_citations:
            stats = self._extract_statistics(citation.surrounding_text)
            results.append(VerificationResult(
                citation_text=citation.citation_text,
                url=citation.url,
                file_path=citation.file_path,
                line_number=citation.line_number,
                surrounding_text=citation.surrounding_text,
                has_specific_statistic=len(stats) > 0,
                claimed_statistics=stats
            ))

        # Phase 0: DOI Existence Validation (NEW)
        if 0 in phases:
            print("\n[Phase 0] Validating DOI existence...")
            urls = [r.url for r in results]

            def progress(done, total):
                print(f"\r  Progress: {done}/{total}", end='', flush=True)

            doi_results = await self.doi_validator.validate_batch(
                urls,
                concurrency=self.doi_concurrency,
                progress_callback=progress
            )
            print()

            for i, doi_result in enumerate(doi_results):
                results[i].doi_result = doi_result
                if doi_result.status == DOIStatus.FABRICATED:
                    results[i].errors.append("DOI does not exist in CrossRef registry (fabricated)")
                    results[i].needs_correction = True
                    # Check if this also has a specific statistic
                    if results[i].has_specific_statistic:
                        results[i].errors.append("Specific statistic claimed without verifiable source")

            fabricated = sum(1 for r in doi_results if r.status == DOIStatus.FABRICATED)
            print(f"  Fabricated DOIs: {fabricated}")

        # Phase 1: URL Verification
        if 1 in phases:
            print("\n[Phase 1] Verifying URLs...")
            urls = [r.url for r in results]

            def progress(done, total):
                print(f"\r  Progress: {done}/{total}", end='', flush=True)

            url_results = await self.url_verifier.verify_batch(
                urls,
                concurrency=self.url_concurrency,
                progress_callback=progress
            )
            print()

            for i, url_result in enumerate(url_results):
                results[i].url_result = url_result
                if url_result.status == URLStatus.BROKEN:
                    results[i].errors.append("URL returns 404")
                    results[i].needs_correction = True

            broken = sum(1 for r in url_results if r.status == URLStatus.BROKEN)
            print(f"  Broken URLs: {broken}")

        # Phase 2: Content Verification
        if 2 in phases:
            print("\n[Phase 2] Verifying content alignment...")
            # Only verify citations that passed Phase 1
            to_verify = []
            indices = []
            for i, r in enumerate(results):
                if not r.url_result or r.url_result.is_valid:
                    to_verify.append({
                        'url': r.url,
                        'surrounding_text': r.surrounding_text
                    })
                    indices.append(i)

            if to_verify:
                content_results = await self.content_verifier.verify_batch(
                    to_verify,
                    concurrency=self.content_concurrency
                )

                for j, content_result in enumerate(content_results):
                    i = indices[j]
                    results[i].content_result = content_result
                    if content_result.alignment_status == AlignmentStatus.WRONG_PAPER:
                        results[i].errors.append("DOI points to unrelated paper")
                        results[i].needs_correction = True
                    elif content_result.alignment_status == AlignmentStatus.MISMATCH:
                        results[i].errors.append("Claim-citation mismatch")
                        results[i].needs_correction = True

                wrong = sum(1 for r in content_results if r.alignment_status == AlignmentStatus.WRONG_PAPER)
                mismatch = sum(1 for r in content_results if r.alignment_status == AlignmentStatus.MISMATCH)
                print(f"  Wrong papers: {wrong}")
                print(f"  Claim mismatches: {mismatch}")

        # Phase 3: Metadata Verification
        if 3 in phases:
            print("\n[Phase 3] Verifying metadata...")
            to_verify = []
            indices = []
            for i, r in enumerate(results):
                if not r.url_result or r.url_result.is_valid:
                    to_verify.append({
                        'citation_text': r.citation_text,
                        'url': r.url
                    })
                    indices.append(i)

            if to_verify:
                metadata_results = await self.metadata_verifier.verify_batch(
                    to_verify,
                    concurrency=self.metadata_concurrency
                )

                for j, metadata_result in enumerate(metadata_results):
                    i = indices[j]
                    results[i].metadata_result = metadata_result
                    for discrepancy in metadata_result.discrepancies:
                        if discrepancy.field == MetadataField.AUTHOR:
                            results[i].errors.append(f"Author error: cited {discrepancy.cited_value}, actual {discrepancy.actual_value}")
                        elif discrepancy.field == MetadataField.YEAR:
                            results[i].errors.append(f"Year error: cited {discrepancy.cited_value}, actual {discrepancy.actual_value}")
                        results[i].needs_correction = True

                author_errors = sum(1 for r in metadata_results if any(
                    d.field == MetadataField.AUTHOR for d in r.discrepancies
                ))
                year_errors = sum(1 for r in metadata_results if any(
                    d.field == MetadataField.YEAR for d in r.discrepancies
                ))
                print(f"  Author errors: {author_errors}")
                print(f"  Year errors: {year_errors}")

        # Final assessment
        print("\n[Final Assessment]")
        self._assess_results(results)

        # Build report
        report = PipelineReport(
            timestamp=datetime.now().isoformat(),
            source_path=str(source_path),
            total_citations=len(all_citations),
            unique_citations=len(unique_citations),
            duplicate_citations=len(duplicates),
            results=results
        )

        # Calculate summary stats
        for r in results:
            if r.error_category == ErrorCategory.VERIFIED_CORRECT:
                report.verified_correct += 1
            elif r.error_category == ErrorCategory.BROKEN_URL:
                report.broken_urls += 1
                report.total_errors += 1
            elif r.error_category == ErrorCategory.FABRICATED_DOI:
                report.fabricated_dois += 1
                report.total_errors += 1
            elif r.error_category == ErrorCategory.FABRICATED_STATISTIC:
                report.fabricated_statistics += 1
                report.total_errors += 1
            elif r.error_category == ErrorCategory.WRONG_PAPER:
                report.wrong_papers += 1
                report.total_errors += 1
            elif r.error_category == ErrorCategory.AUTHOR_ERROR:
                report.author_errors += 1
                report.total_errors += 1
            elif r.error_category == ErrorCategory.YEAR_ERROR:
                report.year_errors += 1
                report.total_errors += 1
            elif r.error_category == ErrorCategory.CLAIM_MISMATCH:
                report.claim_mismatches += 1
                report.total_errors += 1
            elif r.error_category == ErrorCategory.UNABLE_TO_VERIFY:
                report.unable_to_verify += 1

        print(f"\n{'='*50}")
        print(f"VERIFICATION COMPLETE")
        print(f"{'='*50}")
        print(f"Total citations: {report.unique_citations}")
        print(f"Verified correct: {report.verified_correct}")
        print(f"Total errors: {report.total_errors}")
        print(f"Error rate: {report.total_errors/report.unique_citations*100:.1f}%")
        print(f"Unable to verify: {report.unable_to_verify}")

        return report

    def _assess_results(self, results: List[VerificationResult]) -> None:
        """Determine final error category for each result."""
        for r in results:
            # Check for fabricated DOI first (Phase 0)
            if r.doi_result and r.doi_result.status == DOIStatus.FABRICATED:
                # Check if this has a specific statistic
                if r.has_specific_statistic:
                    r.error_category = ErrorCategory.FABRICATED_STATISTIC
                else:
                    r.error_category = ErrorCategory.FABRICATED_DOI
                r.confidence = 0.95
                continue

            # Check for URL errors (Phase 1)
            if r.url_result and r.url_result.status == URLStatus.BROKEN:
                # If DOI validation wasn't run or returned NOT_DOI, this is broken URL
                # If DOI validation returned FABRICATED, we already handled it above
                if r.has_specific_statistic:
                    r.error_category = ErrorCategory.FABRICATED_STATISTIC
                else:
                    r.error_category = ErrorCategory.BROKEN_URL
                r.confidence = 0.95
                continue

            # Check for wrong paper (Phase 2)
            if r.content_result and r.content_result.alignment_status == AlignmentStatus.WRONG_PAPER:
                r.error_category = ErrorCategory.WRONG_PAPER
                r.confidence = r.content_result.confidence
                continue

            # Check for claim mismatch (Phase 2)
            if r.content_result and r.content_result.alignment_status == AlignmentStatus.MISMATCH:
                r.error_category = ErrorCategory.CLAIM_MISMATCH
                r.confidence = r.content_result.confidence
                continue

            # Check for metadata errors (Phase 3)
            if r.metadata_result and r.metadata_result.discrepancies:
                for d in r.metadata_result.discrepancies:
                    if d.field == MetadataField.AUTHOR:
                        r.error_category = ErrorCategory.AUTHOR_ERROR
                        r.confidence = d.confidence
                        break
                    elif d.field == MetadataField.YEAR:
                        r.error_category = ErrorCategory.YEAR_ERROR
                        r.confidence = d.confidence
                        break
                continue

            # If all checks passed
            if r.url_result and r.url_result.is_valid:
                if r.content_result and r.content_result.alignment_status == AlignmentStatus.ALIGNED:
                    r.error_category = ErrorCategory.VERIFIED_CORRECT
                    r.confidence = r.content_result.confidence
                elif not r.content_result:
                    r.error_category = ErrorCategory.UNABLE_TO_VERIFY
                    r.confidence = 0.5
                else:
                    r.error_category = ErrorCategory.VERIFIED_CORRECT
                    r.confidence = 0.6
            else:
                r.error_category = ErrorCategory.UNABLE_TO_VERIFY
                r.confidence = 0.3


def export_report(report: PipelineReport, output_path: str) -> None:
    """Export pipeline report to JSON."""
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(report.to_dict(), f, indent=2, ensure_ascii=False)


def generate_markdown_report(report: PipelineReport, output_path: str) -> None:
    """Generate a human-readable markdown report."""
    lines = [
        "# Citation Verification Report",
        "",
        f"**Generated:** {report.timestamp}",
        f"**Source:** {report.source_path}",
        "",
        "## Summary",
        "",
        f"| Metric | Count |",
        f"|--------|-------|",
        f"| Total citations | {report.total_citations} |",
        f"| Unique citations | {report.unique_citations} |",
        f"| Verified correct | {report.verified_correct} |",
        f"| Total errors | {report.total_errors} |",
        f"| Error rate | {report.total_errors/report.unique_citations*100:.1f}% |",
        "",
        "## Errors by Category",
        "",
        f"| Category | Count |",
        f"|----------|-------|",
        f"| Broken URLs | {report.broken_urls} |",
        f"| Wrong papers | {report.wrong_papers} |",
        f"| Author errors | {report.author_errors} |",
        f"| Year errors | {report.year_errors} |",
        f"| Claim mismatches | {report.claim_mismatches} |",
        "",
        "## Citations Requiring Correction",
        "",
    ]

    for r in report.results:
        if r.needs_correction:
            lines.extend([
                f"### {r.citation_text}",
                "",
                f"**File:** {r.file_path}:{r.line_number}",
                f"**URL:** {r.url}",
                f"**Error:** {r.error_category.value}",
                f"**Details:** {'; '.join(r.errors)}",
                "",
                "---",
                "",
            ])

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))


async def main():
    """Command-line interface for the verification pipeline."""
    parser = argparse.ArgumentParser(
        description='Citation Verification Pipeline',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Verify all .qmd files in a directory
    python verification_pipeline.py ./content/ -o report.json

    # Verify a single file
    python verification_pipeline.py chapter.qmd -o report.json

    # Run only Phase 1 (URL verification)
    python verification_pipeline.py ./content/ --phases 1

    # Generate markdown report
    python verification_pipeline.py ./content/ -o report.json --markdown
        """
    )

    parser.add_argument('path', help='File or directory to verify')
    parser.add_argument('-o', '--output', default='verification_report.json',
                        help='Output JSON file (default: verification_report.json)')
    parser.add_argument('-p', '--pattern', default='*.qmd',
                        help='File pattern for directory search (default: *.qmd)')
    parser.add_argument('--no-recursive', action='store_true',
                        help='Do not search subdirectories')
    parser.add_argument('--phases', type=int, nargs='+', default=[0, 1, 2, 3],
                        choices=[0, 1, 2, 3],
                        help='Phases to run: 0=DOI existence, 1=URL, 2=Content, 3=Metadata (default: all)')
    parser.add_argument('--markdown', action='store_true',
                        help='Also generate markdown report')

    args = parser.parse_args()

    pipeline = VerificationPipeline()

    report = await pipeline.run(
        source_path=args.path,
        file_pattern=args.pattern,
        recursive=not args.no_recursive,
        phases=args.phases
    )

    # Export JSON report
    export_report(report, args.output)
    print(f"\nJSON report exported to: {args.output}")

    # Export markdown report if requested
    if args.markdown:
        md_path = args.output.replace('.json', '.md')
        generate_markdown_report(report, md_path)
        print(f"Markdown report exported to: {md_path}")


if __name__ == '__main__':
    asyncio.run(main())
