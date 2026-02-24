"""Core citation verification logic."""

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional

from .extractors.markdown import Citation
from .validators.doi_resolver import check_doi_exists, DOIResolutionResult
from .validators.crossref import get_crossref_metadata, compare_metadata, CrossRefMetadata
from .validators.prefix_checker import validate_prefix, extract_prefix


class VerificationStatus(Enum):
    """Status of citation verification."""

    VALID = "valid"
    WARNING = "warning"
    INVALID = "invalid"
    ERROR = "error"


class IssueType(Enum):
    """Types of citation issues."""

    DOI_NOT_FOUND = "doi_not_found"  # Pattern 2
    WRONG_PAPER = "wrong_paper"  # Pattern 1
    WRONG_AUTHOR = "wrong_author"  # Pattern 3
    WRONG_YEAR = "wrong_year"  # Pattern 3
    WRONG_PREFIX = "wrong_prefix"  # Pattern 5
    FABRICATED = "fabricated"  # Pattern 4
    NETWORK_ERROR = "network_error"
    UNKNOWN = "unknown"


@dataclass
class VerificationIssue:
    """A specific issue found during verification."""

    type: IssueType
    severity: VerificationStatus
    message: str
    details: Optional[str] = None


@dataclass
class VerificationResult:
    """Result of verifying a single citation."""

    citation: Citation
    status: VerificationStatus
    issues: List[VerificationIssue] = field(default_factory=list)

    # Resolution data
    doi_exists: Optional[bool] = None
    resolution_url: Optional[str] = None

    # Metadata from CrossRef
    crossref_metadata: Optional[CrossRefMetadata] = None

    # Prefix validation
    prefix_validation: Optional[dict] = None

    @property
    def is_valid(self) -> bool:
        return self.status == VerificationStatus.VALID

    @property
    def has_errors(self) -> bool:
        return self.status in [VerificationStatus.INVALID, VerificationStatus.ERROR]


def verify_citation(
    citation: Citation,
    check_resolution: bool = True,
    check_metadata: bool = True,
    check_prefix: bool = True,
) -> VerificationResult:
    """Verify a single citation.

    Args:
        citation: The citation to verify
        check_resolution: Whether to check if DOI resolves
        check_metadata: Whether to fetch and compare CrossRef metadata
        check_prefix: Whether to validate DOI prefix

    Returns:
        VerificationResult with status and any issues found
    """
    result = VerificationResult(
        citation=citation,
        status=VerificationStatus.VALID,
        issues=[],
    )

    # Step 1: Check DOI resolution
    if check_resolution:
        resolution = check_doi_exists(citation.doi)
        result.doi_exists = resolution.exists
        result.resolution_url = resolution.redirect_url

        if not resolution.exists:
            if resolution.error:
                result.issues.append(VerificationIssue(
                    type=IssueType.NETWORK_ERROR,
                    severity=VerificationStatus.ERROR,
                    message=f"Could not verify DOI: {resolution.error}",
                ))
                result.status = VerificationStatus.ERROR
            else:
                result.issues.append(VerificationIssue(
                    type=IssueType.DOI_NOT_FOUND,
                    severity=VerificationStatus.INVALID,
                    message=f"DOI does not exist (HTTP {resolution.status_code})",
                    details=f"DOI: {citation.doi}",
                ))
                result.status = VerificationStatus.INVALID
                # If DOI doesn't exist, can't check metadata
                return result

    # Step 2: Check CrossRef metadata
    if check_metadata and result.doi_exists:
        metadata = get_crossref_metadata(citation.doi)
        result.crossref_metadata = metadata

        if metadata:
            comparison = compare_metadata(
                citation.claimed_author,
                citation.claimed_year,
                metadata
            )

            # Check author match
            if comparison['author_match'] is False:
                result.issues.append(VerificationIssue(
                    type=IssueType.WRONG_AUTHOR,
                    severity=VerificationStatus.INVALID,
                    message=f"Author mismatch",
                    details=f"Claimed: {comparison['author_claimed']}, "
                            f"Actual: {comparison['author_actual']}",
                ))
                if result.status == VerificationStatus.VALID:
                    result.status = VerificationStatus.INVALID

            # Check year match
            if comparison['year_match'] is False:
                # Determine severity based on year difference
                year_diff = abs(
                    (comparison['year_claimed'] or 0) -
                    (comparison['year_actual'] or 0)
                )

                if year_diff == 1:
                    severity = VerificationStatus.WARNING
                    result.issues.append(VerificationIssue(
                        type=IssueType.WRONG_YEAR,
                        severity=severity,
                        message=f"Year off by 1 (minor)",
                        details=f"Claimed: {comparison['year_claimed']}, "
                                f"Actual: {comparison['year_actual']}",
                    ))
                    if result.status == VerificationStatus.VALID:
                        result.status = VerificationStatus.WARNING
                else:
                    result.issues.append(VerificationIssue(
                        type=IssueType.WRONG_YEAR,
                        severity=VerificationStatus.INVALID,
                        message=f"Year mismatch",
                        details=f"Claimed: {comparison['year_claimed']}, "
                                f"Actual: {comparison['year_actual']}",
                    ))
                    result.status = VerificationStatus.INVALID

    # Step 3: Check DOI prefix
    if check_prefix:
        prefix_result = validate_prefix(
            citation.doi,
            citation.claimed_journal
        )
        result.prefix_validation = prefix_result

        if not prefix_result['prefix_valid']:
            result.issues.append(VerificationIssue(
                type=IssueType.WRONG_PREFIX,
                severity=VerificationStatus.INVALID,
                message="DOI prefix doesn't match journal",
                details="; ".join(prefix_result['issues']),
            ))
            result.status = VerificationStatus.INVALID

    return result


def verify_citations(
    citations: List[Citation],
    check_resolution: bool = True,
    check_metadata: bool = True,
    check_prefix: bool = True,
    progress_callback=None,
) -> List[VerificationResult]:
    """Verify multiple citations.

    Args:
        citations: List of citations to verify
        check_resolution: Whether to check DOI resolution
        check_metadata: Whether to check CrossRef metadata
        check_prefix: Whether to validate DOI prefixes
        progress_callback: Optional callback(current, total) for progress

    Returns:
        List of VerificationResult objects
    """
    results = []

    for i, citation in enumerate(citations):
        result = verify_citation(
            citation,
            check_resolution=check_resolution,
            check_metadata=check_metadata,
            check_prefix=check_prefix,
        )
        results.append(result)

        if progress_callback:
            progress_callback(i + 1, len(citations))

    return results


def verify_doi(doi: str) -> VerificationResult:
    """Verify a single DOI (convenience function).

    Args:
        doi: DOI string to verify

    Returns:
        VerificationResult
    """
    citation = Citation(
        doi=doi,
        text="",
        context="",
        line_number=0,
        file_path="",
    )

    return verify_citation(citation)


def summarize_results(results: List[VerificationResult]) -> dict:
    """Summarize verification results.

    Args:
        results: List of verification results

    Returns:
        Summary dict with counts and lists
    """
    summary = {
        'total': len(results),
        'valid': 0,
        'warnings': 0,
        'invalid': 0,
        'errors': 0,
        'issues_by_type': {},
        'invalid_citations': [],
        'warning_citations': [],
    }

    for result in results:
        if result.status == VerificationStatus.VALID:
            summary['valid'] += 1
        elif result.status == VerificationStatus.WARNING:
            summary['warnings'] += 1
            summary['warning_citations'].append(result)
        elif result.status == VerificationStatus.INVALID:
            summary['invalid'] += 1
            summary['invalid_citations'].append(result)
        else:
            summary['errors'] += 1

        # Count issues by type
        for issue in result.issues:
            type_name = issue.type.value
            summary['issues_by_type'][type_name] = \
                summary['issues_by_type'].get(type_name, 0) + 1

    summary['error_rate'] = (
        (summary['invalid'] + summary['errors']) / summary['total'] * 100
        if summary['total'] > 0 else 0
    )

    return summary
