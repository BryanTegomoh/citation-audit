#!/usr/bin/env python3
"""
Citation Rubric Module

Multi-dimensional scoring system for citation verification.
Replaces binary error categorization with per-dimension scores,
enabling fix validation, severity-weighted prioritization, and
before/after comparison when LLMs correct citations.

Part of the Five-Phase Citation Verification Pipeline.

Usage:
    rubric = CitationRubric()
    score = rubric.score(verification_result)
    print(score.composite)        # 0.0-1.0 weighted score
    print(score.worst_dimension)  # "claim_support"
    print(score.to_dict())        # full breakdown

    # Compare before/after a fix
    delta = rubric.compare(score_before, score_after)
    if delta.is_improvement(min_delta=0.15):
        print("Fix accepted")
"""

import json
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Tuple
from enum import Enum


class Dimension(Enum):
    """Rubric dimensions for citation verification."""
    DOI_EXISTENCE = "doi_existence"
    URL_RESOLUTION = "url_resolution"
    TOPIC_ALIGNMENT = "topic_alignment"
    CLAIM_SUPPORT = "claim_support"
    STATISTIC_ACCURACY = "statistic_accuracy"
    AUTHOR_ACCURACY = "author_accuracy"
    YEAR_ACCURACY = "year_accuracy"
    JOURNAL_ACCURACY = "journal_accuracy"
    DIRECTION_OF_EFFECT = "direction_of_effect"


# Descriptions for each dimension (used in reports)
DIMENSION_DESCRIPTIONS = {
    Dimension.DOI_EXISTENCE: "Does the DOI resolve in CrossRef?",
    Dimension.URL_RESOLUTION: "Does the URL return a valid page?",
    Dimension.TOPIC_ALIGNMENT: "Does the paper's topic match the claim's domain?",
    Dimension.CLAIM_SUPPORT: "Does the paper's conclusion support the specific claim?",
    Dimension.STATISTIC_ACCURACY: "Do cited numbers appear in the source?",
    Dimension.AUTHOR_ACCURACY: "Is the first author correct?",
    Dimension.YEAR_ACCURACY: "Is the publication year correct?",
    Dimension.JOURNAL_ACCURACY: "Is the journal name correct?",
    Dimension.DIRECTION_OF_EFFECT: "Does the paper's finding direction match the framing?",
}

# Default weights: claim_support and statistic_accuracy dominate
# because wrong claims are more dangerous than wrong metadata.
DEFAULT_WEIGHTS = {
    Dimension.DOI_EXISTENCE: 0.10,
    Dimension.URL_RESOLUTION: 0.10,
    Dimension.TOPIC_ALIGNMENT: 0.10,
    Dimension.CLAIM_SUPPORT: 0.25,
    Dimension.STATISTIC_ACCURACY: 0.15,
    Dimension.AUTHOR_ACCURACY: 0.10,
    Dimension.YEAR_ACCURACY: 0.05,
    Dimension.JOURNAL_ACCURACY: 0.05,
    Dimension.DIRECTION_OF_EFFECT: 0.10,
}


@dataclass
class DimensionScore:
    """Score for a single rubric dimension."""
    dimension: Dimension
    score: float  # 0.0 (fail) to 1.0 (pass)
    weight: float
    evidence: str  # Why this score was assigned
    phase_source: Optional[str] = None  # Which pipeline phase produced this

    @property
    def weighted_score(self) -> float:
        return self.score * self.weight

    def to_dict(self) -> Dict:
        return {
            'dimension': self.dimension.value,
            'score': self.score,
            'weight': self.weight,
            'weighted_score': round(self.weighted_score, 4),
            'evidence': self.evidence,
            'phase_source': self.phase_source,
        }


@dataclass
class RubricScore:
    """Complete rubric score for a single citation."""
    citation_text: str
    url: str
    file_path: str
    line_number: int
    dimensions: Dict[Dimension, DimensionScore] = field(default_factory=dict)

    @property
    def composite(self) -> float:
        """Weighted composite score across all scored dimensions."""
        if not self.dimensions:
            return 0.0
        total_weight = sum(d.weight for d in self.dimensions.values())
        if total_weight == 0:
            return 0.0
        weighted_sum = sum(d.weighted_score for d in self.dimensions.values())
        return weighted_sum / total_weight

    @property
    def worst_dimension(self) -> Optional[Dimension]:
        """Dimension with the lowest score (highest priority to fix)."""
        if not self.dimensions:
            return None
        return min(self.dimensions.values(), key=lambda d: d.score).dimension

    @property
    def failed_dimensions(self) -> List[Dimension]:
        """Dimensions scoring below 0.5."""
        return [
            dim for dim, ds in self.dimensions.items()
            if ds.score < 0.5
        ]

    @property
    def grade(self) -> str:
        """Letter grade based on composite score."""
        c = self.composite
        if c >= 0.9:
            return "A"
        elif c >= 0.8:
            return "B"
        elif c >= 0.7:
            return "C"
        elif c >= 0.5:
            return "D"
        else:
            return "F"

    def to_dict(self) -> Dict:
        return {
            'citation_text': self.citation_text,
            'url': self.url,
            'file_path': self.file_path,
            'line_number': self.line_number,
            'composite': round(self.composite, 4),
            'grade': self.grade,
            'worst_dimension': self.worst_dimension.value if self.worst_dimension else None,
            'failed_dimensions': [d.value for d in self.failed_dimensions],
            'dimensions': {
                dim.value: ds.to_dict()
                for dim, ds in self.dimensions.items()
            },
        }


@dataclass
class ScoreDelta:
    """Comparison between before and after rubric scores."""
    before: RubricScore
    after: RubricScore
    dimension_deltas: Dict[str, float] = field(default_factory=dict)

    @property
    def composite_delta(self) -> float:
        return self.after.composite - self.before.composite

    @property
    def improved_dimensions(self) -> List[str]:
        return [d for d, v in self.dimension_deltas.items() if v > 0]

    @property
    def degraded_dimensions(self) -> List[str]:
        return [d for d, v in self.dimension_deltas.items() if v < 0]

    def is_improvement(self, min_delta: float = 0.15) -> bool:
        """Check if the fix produced a meaningful improvement."""
        return self.composite_delta >= min_delta

    def to_dict(self) -> Dict:
        return {
            'composite_before': round(self.before.composite, 4),
            'composite_after': round(self.after.composite, 4),
            'composite_delta': round(self.composite_delta, 4),
            'is_improvement': self.is_improvement(),
            'grade_before': self.before.grade,
            'grade_after': self.after.grade,
            'improved_dimensions': self.improved_dimensions,
            'degraded_dimensions': self.degraded_dimensions,
            'dimension_deltas': {
                k: round(v, 4) for k, v in self.dimension_deltas.items()
            },
        }


class CitationRubric:
    """
    Multi-dimensional rubric for scoring citation verification results.

    Maps pipeline phase outputs to dimension scores and computes
    weighted composites for prioritization and fix validation.

    Usage:
        rubric = CitationRubric()

        # Score a single verification result
        score = rubric.score(verification_result)

        # Score and rank a batch
        scores = rubric.score_batch(results)
        ranked = rubric.prioritize(scores)

        # Validate a fix
        delta = rubric.compare(before_score, after_score)
    """

    # Minimum improvement delta to count as a real improvement
    MIN_IMPROVEMENT_DELTA = 0.15

    def __init__(self, weights: Optional[Dict[Dimension, float]] = None):
        """
        Initialize rubric with optional custom weights.

        Args:
            weights: Custom dimension weights. Must sum to 1.0.
                     If None, uses DEFAULT_WEIGHTS.
        """
        self.weights = weights or DEFAULT_WEIGHTS.copy()
        total = sum(self.weights.values())
        if abs(total - 1.0) > 0.01:
            raise ValueError(f"Weights must sum to 1.0, got {total}")

    def score(self, result) -> RubricScore:
        """
        Score a VerificationResult across all rubric dimensions.

        Args:
            result: A VerificationResult from the verification pipeline.

        Returns:
            RubricScore with per-dimension scores and composite.
        """
        rubric_score = RubricScore(
            citation_text=result.citation_text,
            url=result.url,
            file_path=result.file_path,
            line_number=result.line_number,
        )

        rubric_score.dimensions[Dimension.DOI_EXISTENCE] = self._score_doi(result)
        rubric_score.dimensions[Dimension.URL_RESOLUTION] = self._score_url(result)
        rubric_score.dimensions[Dimension.TOPIC_ALIGNMENT] = self._score_topic(result)
        rubric_score.dimensions[Dimension.CLAIM_SUPPORT] = self._score_claim(result)
        rubric_score.dimensions[Dimension.STATISTIC_ACCURACY] = self._score_statistics(result)
        rubric_score.dimensions[Dimension.AUTHOR_ACCURACY] = self._score_author(result)
        rubric_score.dimensions[Dimension.YEAR_ACCURACY] = self._score_year(result)
        rubric_score.dimensions[Dimension.JOURNAL_ACCURACY] = self._score_journal(result)
        rubric_score.dimensions[Dimension.DIRECTION_OF_EFFECT] = self._score_direction(result)

        return rubric_score

    def score_batch(self, results: list) -> List[RubricScore]:
        """Score a list of VerificationResults."""
        return [self.score(r) for r in results]

    def prioritize(self, scores: List[RubricScore]) -> List[RubricScore]:
        """
        Rank scores by composite (worst first) for fix prioritization.

        Returns:
            Scores sorted ascending by composite (worst citations first).
        """
        return sorted(scores, key=lambda s: s.composite)

    def compare(self, before: RubricScore, after: RubricScore) -> ScoreDelta:
        """
        Compare before/after scores to validate a fix.

        Args:
            before: RubricScore before the fix was applied.
            after: RubricScore after the fix was applied.

        Returns:
            ScoreDelta with per-dimension and composite deltas.
        """
        dimension_deltas = {}
        all_dims = set(before.dimensions.keys()) | set(after.dimensions.keys())
        for dim in all_dims:
            before_score = before.dimensions[dim].score if dim in before.dimensions else 0.0
            after_score = after.dimensions[dim].score if dim in after.dimensions else 0.0
            dimension_deltas[dim.value] = after_score - before_score

        return ScoreDelta(
            before=before,
            after=after,
            dimension_deltas=dimension_deltas,
        )

    # --- Dimension scoring functions ---
    # Each maps pipeline phase outputs to a 0.0-1.0 score.

    def _score_doi(self, result) -> DimensionScore:
        """Phase 0: DOI existence."""
        weight = self.weights[Dimension.DOI_EXISTENCE]

        if result.doi_result is None:
            return DimensionScore(
                dimension=Dimension.DOI_EXISTENCE,
                score=0.5,
                weight=weight,
                evidence="Phase 0 not run",
                phase_source="phase_0",
            )

        from doi_validator import DOIStatus
        status = result.doi_result.status

        if status == DOIStatus.EXISTS:
            return DimensionScore(
                dimension=Dimension.DOI_EXISTENCE,
                score=1.0,
                weight=weight,
                evidence="DOI exists in CrossRef",
                phase_source="phase_0",
            )
        elif status == DOIStatus.FABRICATED:
            return DimensionScore(
                dimension=Dimension.DOI_EXISTENCE,
                score=0.0,
                weight=weight,
                evidence="DOI not found in CrossRef (fabricated)",
                phase_source="phase_0",
            )
        elif status == DOIStatus.NOT_DOI:
            return DimensionScore(
                dimension=Dimension.DOI_EXISTENCE,
                score=0.5,
                weight=weight,
                evidence="URL is not a DOI link",
                phase_source="phase_0",
            )
        else:
            return DimensionScore(
                dimension=Dimension.DOI_EXISTENCE,
                score=0.3,
                weight=weight,
                evidence=f"DOI validation inconclusive: {status.value}",
                phase_source="phase_0",
            )

    def _score_url(self, result) -> DimensionScore:
        """Phase 1: URL resolution."""
        weight = self.weights[Dimension.URL_RESOLUTION]

        if result.url_result is None:
            return DimensionScore(
                dimension=Dimension.URL_RESOLUTION,
                score=0.5,
                weight=weight,
                evidence="Phase 1 not run",
                phase_source="phase_1",
            )

        from url_verifier import URLStatus

        if result.url_result.is_valid:
            return DimensionScore(
                dimension=Dimension.URL_RESOLUTION,
                score=1.0,
                weight=weight,
                evidence=f"URL returns {result.url_result.status_code}",
                phase_source="phase_1",
            )
        else:
            return DimensionScore(
                dimension=Dimension.URL_RESOLUTION,
                score=0.0,
                weight=weight,
                evidence=f"URL broken: {result.url_result.status.value}",
                phase_source="phase_1",
            )

    def _score_topic(self, result) -> DimensionScore:
        """Phase 2: Topic alignment (subset of content verification)."""
        weight = self.weights[Dimension.TOPIC_ALIGNMENT]

        if result.content_result is None:
            return DimensionScore(
                dimension=Dimension.TOPIC_ALIGNMENT,
                score=0.5,
                weight=weight,
                evidence="Phase 2 not run",
                phase_source="phase_2",
            )

        from content_verifier import AlignmentStatus
        status = result.content_result.alignment_status

        if status == AlignmentStatus.WRONG_PAPER:
            return DimensionScore(
                dimension=Dimension.TOPIC_ALIGNMENT,
                score=0.0,
                weight=weight,
                evidence="Paper topic does not match claim",
                phase_source="phase_2",
            )
        elif status in (AlignmentStatus.ALIGNED, AlignmentStatus.PARTIAL_MATCH):
            return DimensionScore(
                dimension=Dimension.TOPIC_ALIGNMENT,
                score=1.0,
                weight=weight,
                evidence="Paper topic matches claim domain",
                phase_source="phase_2",
            )
        else:
            return DimensionScore(
                dimension=Dimension.TOPIC_ALIGNMENT,
                score=0.5,
                weight=weight,
                evidence=f"Topic alignment unclear: {status.value}",
                phase_source="phase_2",
            )

    def _score_claim(self, result) -> DimensionScore:
        """Phase 2: Claim-citation support."""
        weight = self.weights[Dimension.CLAIM_SUPPORT]

        if result.content_result is None:
            return DimensionScore(
                dimension=Dimension.CLAIM_SUPPORT,
                score=0.5,
                weight=weight,
                evidence="Phase 2 not run",
                phase_source="phase_2",
            )

        from content_verifier import AlignmentStatus
        status = result.content_result.alignment_status

        score_map = {
            AlignmentStatus.ALIGNED: 1.0,
            AlignmentStatus.PARTIAL_MATCH: 0.6,
            AlignmentStatus.MISMATCH: 0.1,
            AlignmentStatus.WRONG_PAPER: 0.0,
            AlignmentStatus.UNABLE_TO_VERIFY: 0.4,
            AlignmentStatus.REQUIRES_REVIEW: 0.5,
        }

        s = score_map.get(status, 0.5)
        mismatches = result.content_result.mismatches or []

        return DimensionScore(
            dimension=Dimension.CLAIM_SUPPORT,
            score=s,
            weight=weight,
            evidence=f"Alignment: {status.value}" + (
                f"; mismatches: {', '.join(mismatches[:3])}" if mismatches else ""
            ),
            phase_source="phase_2",
        )

    def _score_statistics(self, result) -> DimensionScore:
        """Phase 2: Statistic accuracy (numbers in source)."""
        weight = self.weights[Dimension.STATISTIC_ACCURACY]

        # If the claim has no statistics, this dimension is N/A (full score)
        if not result.has_specific_statistic:
            return DimensionScore(
                dimension=Dimension.STATISTIC_ACCURACY,
                score=1.0,
                weight=weight,
                evidence="No specific statistics in claim",
                phase_source="phase_2",
            )

        if result.content_result is None:
            return DimensionScore(
                dimension=Dimension.STATISTIC_ACCURACY,
                score=0.3,
                weight=weight,
                evidence="Statistics claimed but Phase 2 not run",
                phase_source="phase_2",
            )

        # Check if content verification found the statistics
        mismatches = result.content_result.mismatches or []
        stat_mismatches = [m for m in mismatches if 'not found in paper' in m]

        total_stats = len(result.claimed_statistics)
        missing_stats = len(stat_mismatches)

        if total_stats == 0:
            s = 1.0
        else:
            s = max(0.0, 1.0 - (missing_stats / total_stats))

        return DimensionScore(
            dimension=Dimension.STATISTIC_ACCURACY,
            score=s,
            weight=weight,
            evidence=f"{total_stats - missing_stats}/{total_stats} statistics found in source",
            phase_source="phase_2",
        )

    def _score_author(self, result) -> DimensionScore:
        """Phase 3: Author accuracy."""
        weight = self.weights[Dimension.AUTHOR_ACCURACY]

        if result.metadata_result is None:
            return DimensionScore(
                dimension=Dimension.AUTHOR_ACCURACY,
                score=0.5,
                weight=weight,
                evidence="Phase 3 not run",
                phase_source="phase_3",
            )

        from metadata_verifier import MetadataField

        author_errors = [
            d for d in result.metadata_result.discrepancies
            if d.field == MetadataField.AUTHOR
        ]

        if not author_errors:
            if result.metadata_result.verified:
                return DimensionScore(
                    dimension=Dimension.AUTHOR_ACCURACY,
                    score=1.0,
                    weight=weight,
                    evidence="Author verified correct",
                    phase_source="phase_3",
                )
            else:
                return DimensionScore(
                    dimension=Dimension.AUTHOR_ACCURACY,
                    score=0.5,
                    weight=weight,
                    evidence="Could not fetch metadata to verify author",
                    phase_source="phase_3",
                )
        else:
            d = author_errors[0]
            return DimensionScore(
                dimension=Dimension.AUTHOR_ACCURACY,
                score=0.0,
                weight=weight,
                evidence=f"Cited '{d.cited_value}', actual '{d.actual_value}'",
                phase_source="phase_3",
            )

    def _score_year(self, result) -> DimensionScore:
        """Phase 3: Year accuracy."""
        weight = self.weights[Dimension.YEAR_ACCURACY]

        if result.metadata_result is None:
            return DimensionScore(
                dimension=Dimension.YEAR_ACCURACY,
                score=0.5,
                weight=weight,
                evidence="Phase 3 not run",
                phase_source="phase_3",
            )

        from metadata_verifier import MetadataField

        year_errors = [
            d for d in result.metadata_result.discrepancies
            if d.field == MetadataField.YEAR
        ]

        if not year_errors:
            if result.metadata_result.verified:
                return DimensionScore(
                    dimension=Dimension.YEAR_ACCURACY,
                    score=1.0,
                    weight=weight,
                    evidence="Year verified correct",
                    phase_source="phase_3",
                )
            else:
                return DimensionScore(
                    dimension=Dimension.YEAR_ACCURACY,
                    score=0.5,
                    weight=weight,
                    evidence="Could not fetch metadata to verify year",
                    phase_source="phase_3",
                )
        else:
            d = year_errors[0]
            # Off-by-one year is less severe than off-by-many
            try:
                diff = abs(int(d.cited_value) - int(d.actual_value))
                s = 0.3 if diff == 1 else 0.0
            except ValueError:
                s = 0.0

            return DimensionScore(
                dimension=Dimension.YEAR_ACCURACY,
                score=s,
                weight=weight,
                evidence=f"Cited {d.cited_value}, actual {d.actual_value}",
                phase_source="phase_3",
            )

    def _score_journal(self, result) -> DimensionScore:
        """Phase 3: Journal accuracy."""
        weight = self.weights[Dimension.JOURNAL_ACCURACY]

        if result.metadata_result is None:
            return DimensionScore(
                dimension=Dimension.JOURNAL_ACCURACY,
                score=0.5,
                weight=weight,
                evidence="Phase 3 not run",
                phase_source="phase_3",
            )

        from metadata_verifier import MetadataField

        journal_errors = [
            d for d in result.metadata_result.discrepancies
            if d.field == MetadataField.JOURNAL
        ]

        if not journal_errors:
            if result.metadata_result.verified:
                return DimensionScore(
                    dimension=Dimension.JOURNAL_ACCURACY,
                    score=1.0,
                    weight=weight,
                    evidence="Journal verified correct (or not checked)",
                    phase_source="phase_3",
                )
            else:
                return DimensionScore(
                    dimension=Dimension.JOURNAL_ACCURACY,
                    score=0.5,
                    weight=weight,
                    evidence="Could not fetch metadata to verify journal",
                    phase_source="phase_3",
                )
        else:
            d = journal_errors[0]
            return DimensionScore(
                dimension=Dimension.JOURNAL_ACCURACY,
                score=0.0,
                weight=weight,
                evidence=f"Cited '{d.cited_value}', actual '{d.actual_value}'",
                phase_source="phase_3",
            )

    def _score_direction(self, result) -> DimensionScore:
        """Phase 2: Direction of effect.

        This is the hardest dimension to automate. Currently we infer it
        from content alignment: if the paper exists, the topic matches,
        but there's a mismatch, the direction may be wrong.

        Full direction-of-effect detection requires NLP beyond what the
        current pipeline does, so this scores conservatively.
        """
        weight = self.weights[Dimension.DIRECTION_OF_EFFECT]

        if result.content_result is None:
            return DimensionScore(
                dimension=Dimension.DIRECTION_OF_EFFECT,
                score=0.5,
                weight=weight,
                evidence="Phase 2 not run; direction cannot be assessed",
                phase_source="phase_2",
            )

        from content_verifier import AlignmentStatus
        status = result.content_result.alignment_status

        if status == AlignmentStatus.ALIGNED:
            return DimensionScore(
                dimension=Dimension.DIRECTION_OF_EFFECT,
                score=0.8,
                weight=weight,
                evidence="Content aligned; direction likely correct (requires human confirmation)",
                phase_source="phase_2",
            )
        elif status == AlignmentStatus.MISMATCH:
            # Mismatch could be direction-of-effect issue
            return DimensionScore(
                dimension=Dimension.DIRECTION_OF_EFFECT,
                score=0.3,
                weight=weight,
                evidence="Content mismatch detected; possible direction-of-effect error",
                phase_source="phase_2",
            )
        elif status == AlignmentStatus.WRONG_PAPER:
            return DimensionScore(
                dimension=Dimension.DIRECTION_OF_EFFECT,
                score=0.0,
                weight=weight,
                evidence="Wrong paper; direction of effect cannot be assessed",
                phase_source="phase_2",
            )
        else:
            return DimensionScore(
                dimension=Dimension.DIRECTION_OF_EFFECT,
                score=0.5,
                weight=weight,
                evidence=f"Direction unclear: {status.value}",
                phase_source="phase_2",
            )


def generate_rubric_report(scores: List[RubricScore], output_path: str) -> None:
    """Generate a JSON report with rubric scores for all citations."""
    # Summary statistics
    composites = [s.composite for s in scores]
    grade_counts = {}
    for s in scores:
        grade_counts[s.grade] = grade_counts.get(s.grade, 0) + 1

    # Dimension averages
    dim_averages = {}
    for dim in Dimension:
        dim_scores = [
            s.dimensions[dim].score
            for s in scores
            if dim in s.dimensions
        ]
        if dim_scores:
            dim_averages[dim.value] = round(sum(dim_scores) / len(dim_scores), 4)

    # Most common failure dimensions
    failure_counts = {}
    for s in scores:
        for dim in s.failed_dimensions:
            failure_counts[dim.value] = failure_counts.get(dim.value, 0) + 1

    report = {
        'summary': {
            'total_citations': len(scores),
            'mean_composite': round(sum(composites) / len(composites), 4) if composites else 0,
            'min_composite': round(min(composites), 4) if composites else 0,
            'max_composite': round(max(composites), 4) if composites else 0,
            'grade_distribution': grade_counts,
            'dimension_averages': dim_averages,
            'most_common_failures': dict(
                sorted(failure_counts.items(), key=lambda x: -x[1])
            ),
        },
        'scores': [s.to_dict() for s in scores],
    }

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)


def generate_markdown_rubric_report(scores: List[RubricScore], output_path: str) -> None:
    """Generate a human-readable markdown rubric report."""
    composites = [s.composite for s in scores]
    lines = [
        "# Citation Rubric Report",
        "",
        "## Summary",
        "",
        f"- **Total citations:** {len(scores)}",
        f"- **Mean score:** {sum(composites) / len(composites):.2f}" if composites else "- **Mean score:** N/A",
        f"- **Score range:** {min(composites):.2f} - {max(composites):.2f}" if composites else "",
        "",
        "## Grade Distribution",
        "",
        "| Grade | Count |",
        "|-------|-------|",
    ]

    grade_counts = {}
    for s in scores:
        grade_counts[s.grade] = grade_counts.get(s.grade, 0) + 1
    for grade in ['A', 'B', 'C', 'D', 'F']:
        if grade in grade_counts:
            lines.append(f"| {grade} | {grade_counts[grade]} |")

    lines.extend([
        "",
        "## Dimension Averages",
        "",
        "| Dimension | Avg Score | Description |",
        "|-----------|-----------|-------------|",
    ])

    for dim in Dimension:
        dim_scores = [s.dimensions[dim].score for s in scores if dim in s.dimensions]
        avg = sum(dim_scores) / len(dim_scores) if dim_scores else 0
        lines.append(f"| {dim.value} | {avg:.2f} | {DIMENSION_DESCRIPTIONS[dim]} |")

    # Citations needing attention (sorted worst first)
    ranked = sorted(scores, key=lambda s: s.composite)
    failing = [s for s in ranked if s.composite < 0.5]

    if failing:
        lines.extend([
            "",
            f"## Citations Needing Attention ({len(failing)})",
            "",
        ])
        for s in failing[:20]:  # Cap at 20
            lines.extend([
                f"### {s.citation_text} (Score: {s.composite:.2f}, Grade: {s.grade})",
                "",
                f"**File:** {s.file_path}:{s.line_number}",
                f"**URL:** {s.url}",
                f"**Failed dimensions:** {', '.join(d.value for d in s.failed_dimensions)}",
                "",
                "| Dimension | Score | Evidence |",
                "|-----------|-------|----------|",
            ])
            for dim, ds in s.dimensions.items():
                marker = " **" if ds.score < 0.5 else ""
                lines.append(f"| {dim.value} | {ds.score:.1f}{marker} | {ds.evidence} |")
            lines.extend(["", "---", ""])

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))


def main():
    """CLI for scoring citations with the rubric."""
    import argparse

    parser = argparse.ArgumentParser(
        description='Score citations using the multi-dimensional rubric',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Score from a verification report
    python rubric.py verification_report.json -o rubric_scores.json

    # Generate markdown report
    python rubric.py verification_report.json -o rubric_scores.json --markdown

    # Custom weights (JSON file)
    python rubric.py verification_report.json --weights custom_weights.json
        """
    )

    parser.add_argument('input', help='Input verification report JSON')
    parser.add_argument('-o', '--output', default='rubric_scores.json',
                        help='Output JSON file (default: rubric_scores.json)')
    parser.add_argument('--markdown', action='store_true',
                        help='Also generate markdown report')
    parser.add_argument('--weights', help='Custom weights JSON file')
    parser.add_argument('--min-delta', type=float, default=0.15,
                        help='Minimum improvement delta (default: 0.15)')

    args = parser.parse_args()

    # Load weights if provided
    weights = None
    if args.weights:
        with open(args.weights, 'r') as f:
            raw = json.load(f)
        weights = {Dimension(k): v for k, v in raw.items()}

    rubric = CitationRubric(weights=weights)
    rubric.MIN_IMPROVEMENT_DELTA = args.min_delta

    # Load verification report
    with open(args.input, 'r', encoding='utf-8') as f:
        report_data = json.load(f)

    # Reconstruct minimal result objects for scoring
    # This handles the case where rubric.py is run standalone
    # against a saved verification_report.json
    from _score_from_report import score_from_report_data
    scores = score_from_report_data(report_data, rubric)

    # Export
    generate_rubric_report(scores, args.output)
    print(f"Rubric scores exported to: {args.output}")

    if args.markdown:
        md_path = args.output.replace('.json', '.md')
        generate_markdown_rubric_report(scores, md_path)
        print(f"Markdown report exported to: {md_path}")

    # Print summary
    composites = [s.composite for s in scores]
    print(f"\nSummary:")
    print(f"  Citations scored: {len(scores)}")
    print(f"  Mean score: {sum(composites) / len(composites):.2f}" if composites else "  Mean score: N/A")
    print(f"  Failing (< 0.5): {sum(1 for c in composites if c < 0.5)}")
    print(f"  Passing (>= 0.8): {sum(1 for c in composites if c >= 0.8)}")


if __name__ == '__main__':
    main()
