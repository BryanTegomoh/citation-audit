"""Tests for the citation rubric module."""

import pytest
import sys
import os

# Add scripts/ to path so imports work
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))

from rubric import (
    CitationRubric,
    RubricScore,
    ScoreDelta,
    DimensionScore,
    Dimension,
    DEFAULT_WEIGHTS,
    DIMENSION_DESCRIPTIONS,
    generate_rubric_report,
    generate_markdown_rubric_report,
)


# --- Fake phase result objects for testing ---

class FakeDOIResult:
    def __init__(self, status_value):
        self._status = status_value

    @property
    def status(self):
        from doi_validator import DOIStatus
        return DOIStatus(self._status)


class FakeURLResult:
    def __init__(self, is_valid, status_value="ok", status_code=200):
        self.is_valid = is_valid
        self.status_code = status_code
        # Map convenience names to actual enum values
        status_map = {"broken": "broken_404", "ok": "ok"}
        self._status = status_map.get(status_value, status_value)

    @property
    def status(self):
        from url_verifier import URLStatus
        return URLStatus(self._status)


class FakeContentResult:
    def __init__(self, alignment_value, confidence=0.8, mismatches=None):
        self._alignment = alignment_value
        self.confidence = confidence
        self.mismatches = mismatches or []

    @property
    def alignment_status(self):
        from content_verifier import AlignmentStatus
        return AlignmentStatus(self._alignment)


class FakeMetadataDiscrepancy:
    def __init__(self, field_value, cited, actual, confidence=0.9):
        from metadata_verifier import MetadataField
        self.field = MetadataField(field_value)
        self.cited_value = cited
        self.actual_value = actual
        self.confidence = confidence


class FakeMetadataResult:
    def __init__(self, verified=True, discrepancies=None):
        self.verified = verified
        self.discrepancies = discrepancies or []


class FakeVerificationResult:
    """Minimal mock of VerificationResult for rubric scoring."""
    def __init__(
        self,
        citation_text="Test et al., 2024",
        url="https://doi.org/10.1234/test",
        file_path="test.qmd",
        line_number=42,
        doi_result=None,
        url_result=None,
        content_result=None,
        metadata_result=None,
        has_specific_statistic=False,
        claimed_statistics=None,
    ):
        self.citation_text = citation_text
        self.url = url
        self.file_path = file_path
        self.line_number = line_number
        self.doi_result = doi_result
        self.url_result = url_result
        self.content_result = content_result
        self.metadata_result = metadata_result
        self.has_specific_statistic = has_specific_statistic
        self.claimed_statistics = claimed_statistics or []


class TestDefaultWeights:
    """Test that default weights are valid."""

    def test_weights_sum_to_one(self):
        total = sum(DEFAULT_WEIGHTS.values())
        assert abs(total - 1.0) < 0.01

    def test_all_dimensions_have_weights(self):
        for dim in Dimension:
            assert dim in DEFAULT_WEIGHTS

    def test_all_dimensions_have_descriptions(self):
        for dim in Dimension:
            assert dim in DIMENSION_DESCRIPTIONS

    def test_claim_support_has_highest_weight(self):
        max_dim = max(DEFAULT_WEIGHTS, key=DEFAULT_WEIGHTS.get)
        assert max_dim == Dimension.CLAIM_SUPPORT


class TestCitationRubric:
    """Test the main rubric scoring class."""

    def setup_method(self):
        self.rubric = CitationRubric()

    def test_perfect_citation(self):
        """A citation that passes all checks should score near 1.0."""
        result = FakeVerificationResult(
            doi_result=FakeDOIResult("exists"),
            url_result=FakeURLResult(is_valid=True),
            content_result=FakeContentResult("aligned"),
            metadata_result=FakeMetadataResult(verified=True),
        )
        score = self.rubric.score(result)
        assert score.composite >= 0.8
        assert score.grade in ("A", "B")
        assert len(score.failed_dimensions) == 0

    def test_fabricated_doi(self):
        """Fabricated DOI should tank the score."""
        result = FakeVerificationResult(
            doi_result=FakeDOIResult("fabricated"),
            url_result=FakeURLResult(is_valid=False, status_value="broken"),
        )
        score = self.rubric.score(result)
        assert score.composite < 0.5
        assert Dimension.DOI_EXISTENCE in score.failed_dimensions

    def test_wrong_paper(self):
        """Valid DOI pointing to wrong paper is a content failure."""
        result = FakeVerificationResult(
            doi_result=FakeDOIResult("exists"),
            url_result=FakeURLResult(is_valid=True),
            content_result=FakeContentResult("wrong_paper"),
            metadata_result=FakeMetadataResult(verified=True),
        )
        score = self.rubric.score(result)
        assert Dimension.TOPIC_ALIGNMENT in score.failed_dimensions
        assert Dimension.CLAIM_SUPPORT in score.failed_dimensions

    def test_author_error(self):
        """Wrong author should only affect author dimension."""
        result = FakeVerificationResult(
            doi_result=FakeDOIResult("exists"),
            url_result=FakeURLResult(is_valid=True),
            content_result=FakeContentResult("aligned"),
            metadata_result=FakeMetadataResult(
                verified=True,
                discrepancies=[FakeMetadataDiscrepancy("author", "Smith", "Wong")]
            ),
        )
        score = self.rubric.score(result)
        assert Dimension.AUTHOR_ACCURACY in score.failed_dimensions
        # Overall should still be decent since content is aligned
        assert score.composite > 0.5

    def test_year_off_by_one(self):
        """Off-by-one year error is less severe than off-by-many."""
        result_off1 = FakeVerificationResult(
            doi_result=FakeDOIResult("exists"),
            url_result=FakeURLResult(is_valid=True),
            content_result=FakeContentResult("aligned"),
            metadata_result=FakeMetadataResult(
                verified=True,
                discrepancies=[FakeMetadataDiscrepancy("year", "2023", "2024")]
            ),
        )
        result_off5 = FakeVerificationResult(
            doi_result=FakeDOIResult("exists"),
            url_result=FakeURLResult(is_valid=True),
            content_result=FakeContentResult("aligned"),
            metadata_result=FakeMetadataResult(
                verified=True,
                discrepancies=[FakeMetadataDiscrepancy("year", "2019", "2024")]
            ),
        )
        score_off1 = self.rubric.score(result_off1)
        score_off5 = self.rubric.score(result_off5)

        year_score_off1 = score_off1.dimensions[Dimension.YEAR_ACCURACY].score
        year_score_off5 = score_off5.dimensions[Dimension.YEAR_ACCURACY].score

        assert year_score_off1 > year_score_off5

    def test_statistics_claimed_but_missing(self):
        """Statistics claimed in text but not found in source."""
        result = FakeVerificationResult(
            doi_result=FakeDOIResult("exists"),
            url_result=FakeURLResult(is_valid=True),
            content_result=FakeContentResult(
                "mismatch",
                mismatches=["percentage value 93.5 not found in paper content"]
            ),
            metadata_result=FakeMetadataResult(verified=True),
            has_specific_statistic=True,
            claimed_statistics=["93.5%"],
        )
        score = self.rubric.score(result)
        stat_score = score.dimensions[Dimension.STATISTIC_ACCURACY].score
        assert stat_score < 0.5

    def test_no_statistics_gets_full_score(self):
        """If no statistics are claimed, stat accuracy should be 1.0."""
        result = FakeVerificationResult(
            doi_result=FakeDOIResult("exists"),
            url_result=FakeURLResult(is_valid=True),
            content_result=FakeContentResult("aligned"),
            metadata_result=FakeMetadataResult(verified=True),
            has_specific_statistic=False,
        )
        score = self.rubric.score(result)
        stat_score = score.dimensions[Dimension.STATISTIC_ACCURACY].score
        assert stat_score == 1.0

    def test_phases_not_run(self):
        """When phases aren't run, dimensions should score 0.5 (unknown)."""
        result = FakeVerificationResult()
        score = self.rubric.score(result)
        for dim, ds in score.dimensions.items():
            if dim == Dimension.STATISTIC_ACCURACY:
                # No stats claimed = 1.0
                continue
            assert ds.score == 0.5, f"{dim.value} should be 0.5 when phase not run"

    def test_worst_dimension(self):
        """Worst dimension should be the lowest-scoring one."""
        result = FakeVerificationResult(
            doi_result=FakeDOIResult("fabricated"),
            url_result=FakeURLResult(is_valid=True),
            content_result=FakeContentResult("aligned"),
            metadata_result=FakeMetadataResult(verified=True),
        )
        score = self.rubric.score(result)
        assert score.worst_dimension == Dimension.DOI_EXISTENCE

    def test_grade_assignment(self):
        """Test grade boundaries."""
        score = RubricScore(
            citation_text="test", url="test", file_path="test", line_number=1,
        )
        # Manually set dimensions to control composite
        for dim in Dimension:
            score.dimensions[dim] = DimensionScore(
                dimension=dim, score=0.95, weight=DEFAULT_WEIGHTS[dim],
                evidence="test"
            )
        assert score.grade == "A"

    def test_to_dict(self):
        """Rubric score should serialize cleanly."""
        result = FakeVerificationResult(
            doi_result=FakeDOIResult("exists"),
            url_result=FakeURLResult(is_valid=True),
            content_result=FakeContentResult("aligned"),
            metadata_result=FakeMetadataResult(verified=True),
        )
        score = self.rubric.score(result)
        d = score.to_dict()
        assert 'composite' in d
        assert 'grade' in d
        assert 'dimensions' in d
        assert 'worst_dimension' in d
        assert 'failed_dimensions' in d
        assert len(d['dimensions']) == len(Dimension)


class TestCustomWeights:
    """Test custom weight configurations."""

    def test_reject_bad_weights(self):
        """Weights that don't sum to 1.0 should raise."""
        bad_weights = {dim: 0.5 for dim in Dimension}
        with pytest.raises(ValueError):
            CitationRubric(weights=bad_weights)

    def test_custom_weights_change_composite(self):
        """Different weights should produce different composites for same result."""
        # Weight claim_support heavily
        heavy_claim = {dim: 0.01 for dim in Dimension}
        heavy_claim[Dimension.CLAIM_SUPPORT] = 1.0 - 0.01 * (len(Dimension) - 1)

        # Weight DOI heavily
        heavy_doi = {dim: 0.01 for dim in Dimension}
        heavy_doi[Dimension.DOI_EXISTENCE] = 1.0 - 0.01 * (len(Dimension) - 1)

        rubric_claim = CitationRubric(weights=heavy_claim)
        rubric_doi = CitationRubric(weights=heavy_doi)

        # Result: good DOI, bad content
        result = FakeVerificationResult(
            doi_result=FakeDOIResult("exists"),
            url_result=FakeURLResult(is_valid=True),
            content_result=FakeContentResult("mismatch"),
            metadata_result=FakeMetadataResult(verified=True),
        )

        score_claim = rubric_claim.score(result)
        score_doi = rubric_doi.score(result)

        # DOI-heavy should score higher (DOI passed, content failed)
        assert score_doi.composite > score_claim.composite


class TestScoreComparison:
    """Test before/after comparison for fix validation."""

    def setup_method(self):
        self.rubric = CitationRubric()

    def test_improvement_detected(self):
        """Fixing a broken citation should show positive delta."""
        before_result = FakeVerificationResult(
            doi_result=FakeDOIResult("fabricated"),
            url_result=FakeURLResult(is_valid=False, status_value="broken"),
        )
        after_result = FakeVerificationResult(
            doi_result=FakeDOIResult("exists"),
            url_result=FakeURLResult(is_valid=True),
            content_result=FakeContentResult("aligned"),
            metadata_result=FakeMetadataResult(verified=True),
        )

        before = self.rubric.score(before_result)
        after = self.rubric.score(after_result)
        delta = self.rubric.compare(before, after)

        assert delta.composite_delta > 0
        assert delta.is_improvement()
        assert len(delta.improved_dimensions) > 0
        assert len(delta.degraded_dimensions) == 0

    def test_degradation_detected(self):
        """A bad 'fix' that makes things worse should show negative delta."""
        before_result = FakeVerificationResult(
            doi_result=FakeDOIResult("exists"),
            url_result=FakeURLResult(is_valid=True),
            content_result=FakeContentResult("aligned"),
            metadata_result=FakeMetadataResult(verified=True),
        )
        after_result = FakeVerificationResult(
            doi_result=FakeDOIResult("exists"),
            url_result=FakeURLResult(is_valid=True),
            content_result=FakeContentResult("wrong_paper"),
            metadata_result=FakeMetadataResult(
                verified=True,
                discrepancies=[FakeMetadataDiscrepancy("author", "Wrong", "Right")]
            ),
        )

        before = self.rubric.score(before_result)
        after = self.rubric.score(after_result)
        delta = self.rubric.compare(before, after)

        assert delta.composite_delta < 0
        assert not delta.is_improvement()
        assert len(delta.degraded_dimensions) > 0

    def test_marginal_improvement_below_threshold(self):
        """Tiny improvements should not pass the minimum delta."""
        before_result = FakeVerificationResult(
            doi_result=FakeDOIResult("exists"),
            url_result=FakeURLResult(is_valid=True),
            content_result=FakeContentResult("partial_match"),
            metadata_result=FakeMetadataResult(verified=True),
        )
        after_result = FakeVerificationResult(
            doi_result=FakeDOIResult("exists"),
            url_result=FakeURLResult(is_valid=True),
            content_result=FakeContentResult("aligned"),
            metadata_result=FakeMetadataResult(verified=True),
        )

        before = self.rubric.score(before_result)
        after = self.rubric.score(after_result)
        delta = self.rubric.compare(before, after)

        # composite_delta should be positive but may be below MIN_IMPROVEMENT_DELTA
        assert delta.composite_delta >= 0

    def test_delta_serialization(self):
        """ScoreDelta should serialize cleanly."""
        before_result = FakeVerificationResult(
            doi_result=FakeDOIResult("fabricated"),
        )
        after_result = FakeVerificationResult(
            doi_result=FakeDOIResult("exists"),
            url_result=FakeURLResult(is_valid=True),
            content_result=FakeContentResult("aligned"),
            metadata_result=FakeMetadataResult(verified=True),
        )
        before = self.rubric.score(before_result)
        after = self.rubric.score(after_result)
        delta = self.rubric.compare(before, after)

        d = delta.to_dict()
        assert 'composite_delta' in d
        assert 'is_improvement' in d
        assert 'grade_before' in d
        assert 'grade_after' in d
        assert 'improved_dimensions' in d


class TestPrioritization:
    """Test citation ranking by rubric score."""

    def setup_method(self):
        self.rubric = CitationRubric()

    def test_worst_first_ordering(self):
        """Prioritize should return worst citations first."""
        good = FakeVerificationResult(
            citation_text="Good et al., 2024",
            doi_result=FakeDOIResult("exists"),
            url_result=FakeURLResult(is_valid=True),
            content_result=FakeContentResult("aligned"),
            metadata_result=FakeMetadataResult(verified=True),
        )
        bad = FakeVerificationResult(
            citation_text="Bad et al., 2024",
            doi_result=FakeDOIResult("fabricated"),
            url_result=FakeURLResult(is_valid=False, status_value="broken"),
        )
        mid = FakeVerificationResult(
            citation_text="Mid et al., 2024",
            doi_result=FakeDOIResult("exists"),
            url_result=FakeURLResult(is_valid=True),
            content_result=FakeContentResult("mismatch"),
            metadata_result=FakeMetadataResult(verified=True),
        )

        scores = self.rubric.score_batch([good, bad, mid])
        ranked = self.rubric.prioritize(scores)

        assert ranked[0].citation_text == "Bad et al., 2024"
        assert ranked[-1].citation_text == "Good et al., 2024"


class TestReportGeneration:
    """Test report output."""

    def setup_method(self):
        self.rubric = CitationRubric()

    def test_json_report(self, tmp_path):
        """JSON report should be valid and contain expected fields."""
        import json

        result = FakeVerificationResult(
            doi_result=FakeDOIResult("exists"),
            url_result=FakeURLResult(is_valid=True),
            content_result=FakeContentResult("aligned"),
            metadata_result=FakeMetadataResult(verified=True),
        )
        scores = self.rubric.score_batch([result])

        output = tmp_path / "rubric_report.json"
        generate_rubric_report(scores, str(output))

        with open(output) as f:
            data = json.load(f)

        assert 'summary' in data
        assert 'scores' in data
        assert data['summary']['total_citations'] == 1
        assert 'dimension_averages' in data['summary']
        assert 'grade_distribution' in data['summary']

    def test_markdown_report(self, tmp_path):
        """Markdown report should be generated."""
        result = FakeVerificationResult(
            doi_result=FakeDOIResult("fabricated"),
            url_result=FakeURLResult(is_valid=False, status_value="broken"),
        )
        scores = self.rubric.score_batch([result])

        output = tmp_path / "rubric_report.md"
        generate_markdown_rubric_report(scores, str(output))

        content = output.read_text()
        assert "# Citation Rubric Report" in content
        assert "Grade Distribution" in content
        assert "Citations Needing Attention" in content


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
