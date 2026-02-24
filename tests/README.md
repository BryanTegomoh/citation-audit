# Tests

This directory contains tests for the Citation Verification Toolkit.

## Running Tests

### Install test dependencies

```bash
pip install pytest pytest-cov
```

### Run all tests

```bash
pytest tests/ -v
```

### Run specific test file

```bash
pytest tests/test_extractors.py -v
```

### Run with coverage

```bash
pytest tests/ --cov=src --cov-report=html
```

## Test Categories

- `test_extractors.py` - Tests for citation extraction from various formats
- `test_validators.py` - Tests for DOI validation and metadata checking
- `test_verify.py` - Tests for core verification logic

## Note on Network Tests

Some tests make real network requests to:
- doi.org (for DOI resolution)
- api.crossref.org (for metadata)

These tests may:
- Be slower than unit tests
- Fail if network is unavailable
- Be rate-limited

Consider marking them as integration tests and running separately if needed.

## Test Data

Sample files in `examples/` are used for testing:
- `sample_markdown.md` - Markdown with various citation formats
- `sample_dois.txt` - Plain text DOI list
- `sample_bibtex.bib` - BibTeX entries

## Adding Tests

When adding new features, add corresponding tests:

1. Create test functions with descriptive names
2. Use pytest fixtures for common setup
3. Test both success and failure cases
4. Document any network dependencies
