# Citation Verification Toolkit

**Purpose:** Detect and correct citation errors in medical and scientific content.
**Author:** Bryan Tegomoh, MD, MPH
**License:** MIT

---

## The Problem

Citations that look correct frequently are not. Standard verification (checking whether a URL resolves) catches approximately 21% of errors. The remaining 79% require reading the cited paper and confirming it supports the specific claim.

This toolkit implements a five-phase verification pipeline to catch the full spectrum of citation errors, from fabricated DOIs to valid papers that do not support the attributed claims.

---

## The Five-Phase Pipeline

```
Phase 0: DOI Existence    Does this DOI exist in CrossRef?
         |
Phase 1: URL Resolution   Does the URL return 200 OK?
         |
Phase 2: Content Alignment   Does the paper support the claim?
         |
Phase 3: Metadata Accuracy   Are author/year/journal correct?
         |
Phase 4: Correction        What is the fix?
```

### Error Categories

| Error Type | Phase | Description |
|------------|-------|-------------|
| FABRICATED_DOI | 0 | DOI follows valid format but does not exist |
| BROKEN_URL | 1 | URL returns 404 or fails to resolve |
| WRONG_PAPER | 2 | Valid URL, completely different paper |
| CLAIM_MISMATCH | 2 | Paper exists but does not support claim |
| CITATION_OVERLOADING | 2 | Single citation used for claims from multiple papers |
| STATISTIC_CONFLATION | 2 | Multiple study periods collapsed into one figure |
| AUTHOR_ERROR | 3 | Wrong first author name |
| YEAR_ERROR | 3 | Wrong publication year |

---

## Quick Start

```bash
pip install -r requirements.txt

# Verify all markdown files in a directory
python scripts/verification_pipeline.py ./content/ -o report.json

# Include a human-readable report
python scripts/verification_pipeline.py ./content/ -o report.json --markdown

# Verify a single file
python scripts/verification_pipeline.py paper.md -o report.json
```

---

## Repository Structure

```
citation-audit/
|
|-- scripts/                  Verification pipeline scripts
|   |-- verification_pipeline.py    Main tool (runs full pipeline)
|   |-- citation_extractor.py       Extract citations from markdown
|   |-- doi_validator.py            Phase 0: CrossRef API validation
|   |-- url_verifier.py             Phase 1: HTTP status checking
|   |-- content_verifier.py         Phase 2: Content alignment
|   |-- metadata_verifier.py        Phase 3: Author/year validation
|
|-- src/                      Installable Python package
|   |-- extractors/                 BibTeX, markdown, plaintext parsers
|   |-- validators/                 CrossRef, DOI resolver, prefix checker
|   |-- reporters/                  Markdown report generation
|
|-- data/                     Reference data
|   |-- publisher_prefixes.json     DOI prefix to publisher mapping (90+)
|   |-- journal_patterns.json       Journal name patterns
|
|-- docs/                     Documentation and methodology
|-- papers/                   Research manuscripts
|-- reports/                  Audit reports
|-- examples/                 Sample files
|-- tests/                    Test suite
```

---

## Key Findings

From verification of 838 citations across 22 medical specialty chapters:

- 21% of citation errors are URL-detectable (broken links, failed DOIs)
- 79% require content-level verification (Phase 2+)
- 21 distinct failure modes documented (see [`docs/METHODOLOGY.md`](docs/METHODOLOGY.md))

---

## Limitations

1. Phase 2 (content-claim alignment) requires domain expertise and human judgment
2. Paywalled content limits automated verification
3. Tested primarily with English-language citations
4. CrossRef API has rate limits for high-volume verification

---

## Citation

```bibtex
@misc{tegomoh2026citation,
  title={Five-Phase Citation Verification Pipeline},
  author={Tegomoh, Bryan},
  year={2026},
  url={https://github.com/BryanTegomoh/citation-audit}
}
```

---

## License

MIT License. Free for academic and commercial use.
