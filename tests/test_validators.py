"""Tests for DOI validators."""

import pytest

from src.validators.prefix_checker import (
    extract_prefix,
    get_publisher_for_prefix,
    get_expected_prefix_for_journal,
    validate_prefix,
)
from src.validators.doi_resolver import check_doi_exists
from src.validators.crossref import get_crossref_metadata


class TestPrefixChecker:
    """Test DOI prefix validation."""

    def test_extract_prefix(self):
        """Test prefix extraction."""
        assert extract_prefix("10.1038/nature21056") == "10.1038"
        assert extract_prefix("10.1001/jama.2020.1234") == "10.1001"
        assert extract_prefix("https://doi.org/10.1056/NEJMoa2035389") == "10.1056"

        # Invalid DOI
        assert extract_prefix("invalid-doi") is None

    def test_get_publisher_for_prefix(self):
        """Test publisher lookup."""
        assert "Nature" in get_publisher_for_prefix("10.1038")
        assert "JAMA" in get_publisher_for_prefix("10.1001")
        assert "NEJM" in get_publisher_for_prefix("10.1056")

        # Unknown prefix
        assert get_publisher_for_prefix("10.9999") is None

    def test_get_expected_prefix_for_journal(self):
        """Test journal to prefix mapping."""
        assert get_expected_prefix_for_journal("Nature Medicine") == "10.1038"
        assert get_expected_prefix_for_journal("JAMA") == "10.1001"
        assert get_expected_prefix_for_journal("lancet") == "10.1016"  # case insensitive

        # Unknown journal
        assert get_expected_prefix_for_journal("Unknown Journal") is None

    def test_validate_prefix_match(self):
        """Test prefix validation with journal match."""
        # Correct match
        result = validate_prefix("10.1038/nature21056", "Nature")
        assert result['prefix_valid'] is True
        assert result['journal_match'] is True

        # Mismatch
        result = validate_prefix("10.1001/jama.2020.1234", "Nature Medicine")
        assert result['prefix_valid'] is False
        assert result['journal_match'] is False
        assert len(result['issues']) > 0


class TestDOIResolver:
    """Test DOI resolution checking."""

    def test_check_valid_doi(self):
        """Test checking a valid DOI."""
        # This makes a real network request - mark as slow/integration test
        result = check_doi_exists("10.1038/nature21056")

        # Should exist (Esteva et al. 2017 dermatology paper)
        assert result.exists is True
        assert result.status_code in [200, 301, 302, 303]

    def test_check_invalid_doi(self):
        """Test checking an invalid DOI."""
        result = check_doi_exists("10.9999/fake.doi.12345")

        # Should not exist
        assert result.exists is False
        assert result.status_code == 404


    def test_bot_blocking_publisher_doi_exists(self):
        """Regression: NEJM returns 403 to bots; the DOI is still real.

        Polack et al. 2020 (BNT162b2 trial) must not be flagged fabricated.
        """
        result = check_doi_exists("10.1056/NEJMoa2034577")
        assert result.exists is True
        assert result.redirect_url and "nejm.org" in result.redirect_url

    def test_accepts_url_and_doi_prefix(self):
        assert check_doi_exists("https://doi.org/10.1038/nature21056").exists
        assert check_doi_exists("doi:10.1038/nature21056").exists

    def test_registry_error_is_not_fabricated(self, monkeypatch):
        """A 5xx from the registry is unknown, never a 404 'fabricated'."""
        import src.validators.doi_resolver as dr

        class Resp:
            status_code = 503
            def json(self):
                raise ValueError

        monkeypatch.setattr(dr.requests, "get", lambda *a, **k: Resp())
        result = dr.check_doi_exists("10.1038/nature21056")
        assert result.exists is False
        assert result.status_code == 503
        assert result.error


class TestCrossRefAPI:
    """Test CrossRef metadata retrieval."""

    def test_get_metadata_valid_doi(self):
        """Test fetching metadata for valid DOI."""
        # Real network request
        metadata = get_crossref_metadata("10.1038/nature21056")

        if metadata:  # May fail if network/API unavailable
            assert "Esteva" in metadata.first_author
            assert metadata.year == 2017
            assert "Nature" in metadata.journal

    def test_get_metadata_invalid_doi(self):
        """Test fetching metadata for invalid DOI."""
        metadata = get_crossref_metadata("10.9999/fake.doi.12345")

        # Should return None
        assert metadata is None


if __name__ == '__main__':
    pytest.main([__file__, '-v'])


class TestPipelineDOIValidator:
    """Phase 0 must not call registered non-Crossref DOIs fabricated."""

    def test_datacite_doi_is_not_fabricated(self):
        import asyncio, os, sys
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
        from doi_validator import DOIValidator, DOIStatus

        v = DOIValidator()
        # A Zenodo (DataCite) DOI that Crossref does not hold.
        res = asyncio.run(v.validate_doi("10.5281/zenodo.3233853"))
        assert res.status == DOIStatus.EXISTS

    def test_fake_doi_still_fabricated(self):
        import asyncio, os, sys
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
        from doi_validator import DOIValidator, DOIStatus

        res = asyncio.run(DOIValidator().validate_doi("10.9999/fake.doi.12345"))
        assert res.status == DOIStatus.FABRICATED
