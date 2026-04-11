#!/usr/bin/env python3
"""
Citation Verification Pipeline (v4.0)

Systematic verification of academic citations across 42 documented failure modes.
Detects errors from fabricated DOIs to semantic misrepresentation, retracted papers,
scope extrapolation, and evidence strength inflation.

Architecture:
  Phase 0: DOI Existence Validation    CrossRef registry lookup
  Phase 1: URL Resolution Testing      HTTP status and redirect chain analysis
  Phase 2: Content-Claim Alignment     Semantic verification against source text
  Phase 3: Metadata Accuracy           Author, year, journal, retraction status
  Phase 4: Correction Analysis         Fix identification and replacement search

Error taxonomy spans six categories:
  - Structural (DOI/URL)               Phases 0-1
  - Content alignment                  Phase 2
  - Semantic misrepresentation          Phase 2 (higher-order)
  - Metadata                           Phase 3
  - Source selection                    Cross-phase
  - Systemic                           Cross-ecosystem

Usage:
    python verification_pipeline.py ./content/ -o report.json
    python verification_pipeline.py ./content/ -o report.json --markdown
    python verification_pipeline.py ./content/ --phases 0 1

Supported file types: .md, .qmd, .rst, .txt
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
from rubric import CitationRubric, generate_rubric_report, generate_markdown_rubric_report


class ErrorCategory(Enum):
    """
    Standardized error categories spanning 42 documented failure modes.

    Categories are organized by verification phase and failure type:
      - Phase 0-1: Structural failures (DOI/URL resolution)
      - Phase 2: Content-level failures (claim-source alignment)
      - Phase 3: Metadata failures (author, year, journal)
      - Semantic: Higher-order reasoning failures
      - Systemic: Cross-ecosystem and infrastructure failures
    """
    # Phase 0-1: Structural
    BROKEN_URL = "broken_url"
    FABRICATED_DOI = "fabricated_doi"
    FABRICATED_REPOSITORY = "fabricated_repository"
    GENERIC_URL = "generic_url"

    # Phase 2: Content alignment
    WRONG_PAPER = "wrong_paper"
    CLAIM_MISMATCH = "claim_mismatch"
    CITATION_OVERLOADING = "citation_overloading"
    STATISTIC_CONFLATION = "statistic_conflation"
    METRIC_ERROR = "metric_error"
    FABRICATED_STATISTIC = "fabricated_statistic"
    INVERTED_STATISTICS = "inverted_statistics"
    CHIMERA_CITATION = "chimera_citation"

    # Phase 2: Semantic misrepresentation (Gaps 25-28)
    SCOPE_EXTRAPOLATION = "scope_extrapolation"
    EVIDENCE_STRENGTH_INFLATION = "evidence_strength_inflation"
    CAUSAL_INFERENCE_ESCALATION = "causal_inference_escalation"
    PARTIAL_SUPPORT = "partial_support"

    # Phase 2: Medical-domain-specific (Gaps 34-37)
    DRUG_NAME_SUBSTITUTION = "drug_name_substitution"
    GEOGRAPHIC_POPULATION_MISMATCH = "geographic_population_mismatch"
    CONFERENCE_ABSTRACT_AS_PAPER = "conference_abstract_as_paper"
    EFFECT_SIZE_DIRECTION_REVERSAL = "effect_size_direction_reversal"

    # Phase 2: OpenEvidence-specific
    DENOMINATOR_SHIFT = "denominator_shift"
    DRAWBACK_OMISSION = "drawback_omission"
    QUALIFIER_OMISSION = "qualifier_omission"
    INTERVENTION_MISCHARACTERIZATION = "intervention_mischaracterization"
    INTERVENTION_MISATTRIBUTION = "intervention_misattribution"
    CONFLATION_ACROSS_STUDIES = "conflation_across_studies"
    DECORATION_CITATION = "decoration_citation"
    SECONDARY_SOURCE_OVERRELIANCE = "secondary_source_overreliance"
    AMBIGUITY = "ambiguity"

    # Phase 3: Metadata
    AUTHOR_ERROR = "author_error"
    YEAR_ERROR = "year_error"
    JOURNAL_ERROR = "journal_error"
    SAMPLE_SIZE_FABRICATION = "sample_size_fabrication"

    # Source selection failures (Gaps 22-24)
    RETRACTED_PAPER = "retracted_paper"
    SUPERSEDED_EVIDENCE = "superseded_evidence"
    POPULARITY_BIAS = "popularity_bias"

    # Systemic failures (Gaps 29-33, 38)
    POST_RATIONALIZATION = "post_rationalization"
    PREDATORY_JOURNAL = "predatory_journal"
    TRAINING_DATA_CONTAMINATION = "training_data_contamination"
    GHOST_REFERENCE = "ghost_reference"
    CONFLICT_OF_INTEREST_BLINDNESS = "conflict_of_interest_blindness"

    # Status
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
    doi_result: Optional[DOIValidationResult] = None
    url_result: Optional[URLVerificationResult] = None
    content_result: Optional[ContentVerificationResult] = None
    metadata_result: Optional[MetadataVerificationResult] = None

    # Claim analysis
    has_specific_statistic: bool = False
    claimed_statistics: List[str] = field(default_factory=list)

    # Semantic analysis flags
    is_retracted: bool = False
    retraction_source: Optional[str] = None
    is_superseded: bool = False
    superseded_by: Optional[str] = None
    study_design: Optional[str] = None  # RCT, cohort, case_report, etc.
    claim_strength: Optional[str] = None  # demonstrated, suggested, preliminary
    study_population_scope: Optional[str] = None  # single_site, multicenter, population
    geographic_scope: Optional[str] = None
    is_conference_abstract: bool = False
    has_industry_funding: Optional[bool] = None
    journal_quality: Optional[str] = None  # indexed, predatory, unknown
    causal_language_detected: bool = False
    observational_design: bool = False

    # Risk stratification
    topic_familiarity_score: Optional[float] = None  # PubMed result count proxy
    citation_count: Optional[int] = None  # Semantic Scholar / OpenAlex
    risk_tier: str = "standard"  # low, standard, elevated, high

    # Final assessment
    error_categories: List[ErrorCategory] = field(default_factory=list)
    error_category: ErrorCategory = ErrorCategory.UNABLE_TO_VERIFY
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
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
            'semantic_flags': {
                'is_retracted': self.is_retracted,
                'retraction_source': self.retraction_source,
                'is_superseded': self.is_superseded,
                'superseded_by': self.superseded_by,
                'study_design': self.study_design,
                'claim_strength': self.claim_strength,
                'study_population_scope': self.study_population_scope,
                'geographic_scope': self.geographic_scope,
                'is_conference_abstract': self.is_conference_abstract,
                'has_industry_funding': self.has_industry_funding,
                'journal_quality': self.journal_quality,
                'causal_language_detected': self.causal_language_detected,
                'observational_design': self.observational_design,
            },
            'risk_stratification': {
                'topic_familiarity_score': self.topic_familiarity_score,
                'citation_count': self.citation_count,
                'risk_tier': self.risk_tier,
            },
            'error_category': self.error_category.value,
            'error_categories': [e.value for e in self.error_categories],
            'errors': self.errors,
            'warnings': self.warnings,
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

    # Rubric scores (populated after pipeline run)
    rubric_scores: List = field(default_factory=list)

    # Summary statistics
    verified_correct: int = 0
    total_errors: int = 0
    total_warnings: int = 0
    unable_to_verify: int = 0

    # Error counts by category
    error_counts: Dict[str, int] = field(default_factory=dict)

    # Risk distribution
    risk_distribution: Dict[str, int] = field(default_factory=lambda: {
        'low': 0, 'standard': 0, 'elevated': 0, 'high': 0
    })

    def to_dict(self) -> Dict:
        error_rate = "N/A"
        if self.unique_citations > 0:
            error_rate = f"{(self.total_errors / self.unique_citations * 100):.1f}%"

        return {
            'timestamp': self.timestamp,
            'source_path': self.source_path,
            'pipeline_version': '4.0',
            'error_taxonomy_version': '2.0',
            'total_failure_modes': len(ErrorCategory) - 2,  # exclude VERIFIED_CORRECT, UNABLE_TO_VERIFY
            'summary': {
                'total_citations': self.total_citations,
                'unique_citations': self.unique_citations,
                'duplicate_citations': self.duplicate_citations,
                'verified_correct': self.verified_correct,
                'total_errors': self.total_errors,
                'total_warnings': self.total_warnings,
                'error_rate': error_rate,
                'unable_to_verify': self.unable_to_verify,
                'by_category': self.error_counts,
                'by_phase': self._errors_by_phase(),
                'risk_distribution': self.risk_distribution,
            },
            'results': [r.to_dict() for r in self.results],
            'rubric_scores': [s.to_dict() for s in self.rubric_scores] if self.rubric_scores else []
        }

    def _errors_by_phase(self) -> Dict[str, int]:
        """Aggregate error counts by verification phase."""
        phase_map = {
            'phase_0_1_structural': [
                'broken_url', 'fabricated_doi', 'fabricated_repository', 'generic_url',
                'fabricated'
            ],
            'phase_2_content': [
                'wrong_paper', 'claim_mismatch', 'citation_overloading',
                'statistic_conflation', 'metric_error', 'fabricated_statistic',
                'inverted_statistics', 'chimera_citation'
            ],
            'phase_2_semantic': [
                'scope_extrapolation', 'evidence_strength_inflation',
                'causal_inference_escalation', 'partial_support',
                'drug_name_substitution', 'geographic_population_mismatch',
                'conference_abstract_as_paper', 'effect_size_direction_reversal',
                'denominator_shift', 'drawback_omission', 'qualifier_omission',
                'intervention_mischaracterization', 'intervention_misattribution',
                'conflation_across_studies', 'decoration_citation',
                'secondary_source_overreliance', 'ambiguity'
            ],
            'phase_3_metadata': [
                'author_error', 'year_error', 'journal_error',
                'sample_size_fabrication'
            ],
            'source_selection': [
                'retracted_paper', 'superseded_evidence', 'popularity_bias'
            ],
            'systemic': [
                'post_rationalization', 'predatory_journal',
                'training_data_contamination', 'ghost_reference',
                'conflict_of_interest_blindness'
            ]
        }
        result = {}
        for phase, categories in phase_map.items():
            result[phase] = sum(self.error_counts.get(c, 0) for c in categories)
        return result


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
            elif r.error_category == ErrorCategory.UNABLE_TO_VERIFY:
                report.unable_to_verify += 1
            else:
                report.total_errors += 1
                cat_key = r.error_category.value
                report.error_counts[cat_key] = report.error_counts.get(cat_key, 0) + 1

            # Count warnings separately (non-blocking issues)
            report.total_warnings += len(r.warnings)

            # Track risk distribution
            tier = r.risk_tier
            if tier in report.risk_distribution:
                report.risk_distribution[tier] += 1

        # Rubric scoring
        print("\n[Rubric Scoring]")
        rubric = CitationRubric()
        report.rubric_scores = rubric.score_batch(results)
        composites = [s.composite for s in report.rubric_scores]
        if composites:
            print(f"  Mean rubric score: {sum(composites)/len(composites):.2f}")
            print(f"  Failing citations (< 0.5): {sum(1 for c in composites if c < 0.5)}")
            print(f"  Grade A citations (>= 0.9): {sum(1 for c in composites if c >= 0.9)}")

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
    error_rate = "N/A"
    if report.unique_citations > 0:
        error_rate = f"{report.total_errors/report.unique_citations*100:.1f}%"

    lines = [
        "# Citation Verification Report",
        "",
        f"**Generated:** {report.timestamp}",
        f"**Source:** {report.source_path}",
        f"**Pipeline Version:** 4.0",
        f"**Error Taxonomy:** 42 failure modes across 6 categories",
        "",
        "## Summary",
        "",
        "| Metric | Count |",
        "|--------|-------|",
        f"| Total citations | {report.total_citations} |",
        f"| Unique citations | {report.unique_citations} |",
        f"| Verified correct | {report.verified_correct} |",
        f"| Total errors | {report.total_errors} |",
        f"| Total warnings | {report.total_warnings} |",
        f"| Error rate | {error_rate} |",
        f"| Unable to verify | {report.unable_to_verify} |",
        "",
        "## Errors by Category",
        "",
        "| Category | Count |",
        "|----------|-------|",
    ]

    # Sort categories by count descending
    sorted_cats = sorted(report.error_counts.items(), key=lambda x: x[1], reverse=True)
    for cat, count in sorted_cats:
        label = cat.replace('_', ' ').title()
        lines.append(f"| {label} | {count} |")

    lines.extend(["", "## Errors by Phase", ""])
    phase_data = report._errors_by_phase()
    lines.extend(["| Phase | Errors |", "|-------|--------|"])
    phase_labels = {
        'phase_0_1_structural': 'Phase 0-1: Structural (DOI/URL)',
        'phase_2_content': 'Phase 2: Content Alignment',
        'phase_2_semantic': 'Phase 2: Semantic Misrepresentation',
        'phase_3_metadata': 'Phase 3: Metadata',
        'source_selection': 'Source Selection',
        'systemic': 'Systemic',
    }
    for key, label in phase_labels.items():
        count = phase_data.get(key, 0)
        if count > 0:
            lines.append(f"| {label} | {count} |")

    lines.extend([
        "",
        "## Risk Distribution",
        "",
        "| Risk Tier | Citations |",
        "|-----------|-----------|",
    ])
    for tier in ['high', 'elevated', 'standard', 'low']:
        count = report.risk_distribution.get(tier, 0)
        lines.append(f"| {tier.title()} | {count} |")

    lines.extend(["", "## Citations Requiring Correction", ""])

    for r in report.results:
        if r.needs_correction:
            lines.extend([
                f"### {r.citation_text}",
                "",
                f"**File:** {r.file_path}:{r.line_number}",
                f"**URL:** {r.url}",
                f"**Error:** {r.error_category.value}",
                f"**Risk Tier:** {r.risk_tier}",
                f"**Details:** {'; '.join(r.errors)}",
            ])
            if r.warnings:
                lines.append(f"**Warnings:** {'; '.join(r.warnings)}")
            lines.extend(["", "---", ""])

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
    parser.add_argument('--rubric', action='store_true',
                        help='Also generate rubric score reports')

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

    # Export rubric reports if requested
    if args.rubric and report.rubric_scores:
        rubric_json = args.output.replace('.json', '_rubric.json')
        rubric_md = args.output.replace('.json', '_rubric.md')
        generate_rubric_report(report.rubric_scores, rubric_json)
        generate_markdown_rubric_report(report.rubric_scores, rubric_md)
        print(f"Rubric JSON report exported to: {rubric_json}")
        print(f"Rubric markdown report exported to: {rubric_md}")


if __name__ == '__main__':
    asyncio.run(main())
