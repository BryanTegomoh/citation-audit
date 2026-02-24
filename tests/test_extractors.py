"""Tests for citation extractors."""

import pytest
from pathlib import Path

from src.extractors.markdown import (
    extract_from_markdown,
    extract_author_year,
    clean_doi,
)
from src.extractors.plaintext import extract_from_plaintext, extract_from_string


class TestMarkdownExtractor:
    """Test markdown citation extraction."""

    def test_extract_author_year(self):
        """Test author and year extraction."""
        # Standard format
        author, year = extract_author_year("Smith et al., 2020")
        assert author == "Smith"
        assert year == 2020

        # Parentheses format
        author, year = extract_author_year("Jones (2019)")
        assert author == "Jones"
        assert year == 2019

        # No match
        author, year = extract_author_year("No citation here")
        assert author is None
        assert year is None

    def test_clean_doi(self):
        """Test DOI cleaning."""
        # Remove trailing punctuation
        assert clean_doi("10.1038/nature21056.") == "10.1038/nature21056"
        assert clean_doi("10.1038/nature21056,") == "10.1038/nature21056"

        # Remove URL encoding
        assert clean_doi("10.1038%2Fnature21056") == "10.1038/nature21056"

        # Remove unbalanced parentheses
        assert clean_doi("10.1038/nature21056)") == "10.1038/nature21056"

    def test_extract_from_sample_markdown(self):
        """Test extraction from sample markdown file."""
        sample_file = Path(__file__).parent.parent / "examples" / "sample_markdown.md"

        if sample_file.exists():
            citations = extract_from_markdown(str(sample_file))

            # Should find multiple citations
            assert len(citations) > 0

            # Check that DOIs are extracted
            dois = [c.doi for c in citations]
            assert "10.1038/nature21056" in dois

            # Check that author/year are extracted where possible
            for citation in citations:
                if citation.text:
                    # At least some should have extracted metadata
                    pass


class TestPlaintextExtractor:
    """Test plaintext DOI extraction."""

    def test_extract_from_string(self):
        """Test DOI extraction from string."""
        text = "Check out 10.1038/nature21056 and https://doi.org/10.1126/science.aax2342"
        dois = extract_from_string(text)

        assert len(dois) == 2
        assert "10.1038/nature21056" in dois
        assert "10.1126/science.aax2342" in dois

    def test_extract_with_prefix(self):
        """Test extraction with doi: prefix."""
        text = "See doi:10.1038/nature21056"
        dois = extract_from_string(text)

        assert len(dois) == 1
        assert dois[0] == "10.1038/nature21056"

    def test_skip_comments(self):
        """Test that comments are skipped."""
        # Would need a temp file for this test
        pass


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
