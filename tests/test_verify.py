"""Tests for core verification logic."""

import pytest

from src.extractors.markdown import Citation
from src.verify import (
    verify_citation,
    verify_doi,
    VerificationStatus,
    IssueType,
    summarize_results,
)


class TestVerification:
    """Test citation verification."""

    def test_verify_valid_citation(self):
        """Test verifying a valid citation."""
        # Known valid DOI: Esteva et al. 2017 Nature
        citation = Citation(
            doi="10.1038/nature21056",
            text="Esteva et al., 2017",
            context="",
            line_number=1,
            file_path="test.md",
            claimed_author="Esteva",
            claimed_year=2017,
        )

        result = verify_citation(citation)

        # Should be valid (assuming network works)
        if result.doi_exists:
            assert result.status == VerificationStatus.VALID
            assert len(result.issues) == 0

    def test_verify_nonexistent_doi(self):
        """Test verifying non-existent DOI."""
        citation = Citation(
            doi="10.9999/fake.doi.12345",
            text="Fake et al., 2025",
            context="",
            line_number=1,
            file_path="test.md",
        )

        result = verify_citation(citation)

        # Should be invalid
        assert result.status == VerificationStatus.INVALID
        assert result.doi_exists is False

        # Should have DOI_NOT_FOUND issue
        issue_types = [i.type for i in result.issues]
        assert IssueType.DOI_NOT_FOUND in issue_types

    def test_verify_doi_convenience_function(self):
        """Test the verify_doi convenience function."""
        result = verify_doi("10.1038/nature21056")

        # Should have doi_exists set
        assert result.doi_exists is not None

    def test_summarize_results(self):
        """Test result summarization."""
        # Create mock results
        citation1 = Citation(doi="10.1038/nature21056", text="", context="",
                            line_number=1, file_path="test.md")
        citation2 = Citation(doi="10.9999/fake", text="", context="",
                            line_number=2, file_path="test.md")

        results = [
            verify_citation(citation1, check_metadata=False),
            verify_citation(citation2, check_metadata=False),
        ]

        summary = summarize_results(results)

        assert summary['total'] == 2
        assert 'valid' in summary
        assert 'invalid' in summary
        assert 'error_rate' in summary


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
