# Contributing to Citation Hallucination Audit

Thank you for your interest in improving citation verification for academic literature.

## Ways to Contribute

### Report New Hallucination Patterns

If you discover a new type of citation error not covered in our documentation:

1. Document the pattern with a specific example
2. Explain how you detected it
3. Suggest a detection method
4. Open an issue or submit a PR to `docs/hallucination-patterns.md`

### Add Publisher Prefixes

The `data/publisher_prefixes.json` file maps DOI prefixes to publishers. To add missing publishers:

1. Find the DOI prefix (e.g., `10.1234`)
2. Identify the publisher name
3. Add an entry to the JSON file
4. Include a source link if possible

### Improve Detection Logic

The validators in `src/validators/` implement detection algorithms. Improvements welcome:

- Better author name matching (handling variations, initials)
- Year extraction from various citation formats
- New validation checks

### Add Input Format Support

Currently supported: Markdown, BibTeX, plain text DOI lists

To add a new format:

1. Create a new extractor in `src/extractors/`
2. Implement the `extract_citations(file_path)` function
3. Return a list of `Citation` objects
4. Add tests in `tests/test_extractors.py`

### Improve Documentation

- Fix typos or unclear explanations
- Add more examples to case studies
- Translate documentation to other languages

## Development Setup

```bash
# Clone the repository
git clone <repo-url>
cd citation-hallucination-audit

# Create virtual environment
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Install in development mode
pip install -e .
pip install pytest pytest-cov

# Run tests
pytest tests/ -v
```

## Code Style

- Use Python type hints where practical
- Follow PEP 8 conventions
- Add docstrings to public functions
- Keep functions focused and testable

## Pull Request Process

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/your-feature`)
3. Make your changes
4. Add or update tests
5. Run `pytest` to ensure tests pass
6. Commit with a clear message
7. Push and open a PR

## Questions?

Open an issue for questions about contributing.
