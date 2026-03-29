# Citation Verification Toolkit

**Purpose:** Detect and correct citation errors in medical and scientific content.
**Author:** Bryan Tegomoh, MD, MPH
**License:** MIT

---

## The Problem

Citations that look correct frequently are not. Standard verification (checking whether a URL resolves) catches approximately 21% of errors. The remaining 79% require reading the cited paper and confirming it supports the specific claim.

This toolkit implements a five-phase verification pipeline to catch the full spectrum of citation errors, from fabricated DOIs to valid papers that do not support the attributed claims.

It can also audit AI-generated medical coding output by checking whether suggested E/M, CPT, and ICD-10 codes are supported by the clinical transcript and structured documentation.

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

# Verify with rubric scoring (JSON + markdown rubric reports)
python scripts/verification_pipeline.py ./content/ -o report.json --rubric

# Verify a single file
python scripts/verification_pipeline.py paper.md -o report.json

# Audit AI-generated medical coding for a sample visit transcript
python scripts/coding_audit.py examples/coding_sample.json
```

---

## Coding Intelligence Integration

OpenEvidence Coding Intelligence can generate E/M levels, CPT procedure codes, and ICD-10 diagnoses from visit transcripts. This repository is a complementary audit layer, not a competing coding engine: it reviews AI-generated codes for supportability and flags places where human review is still required.

The coding audit module in [`src/coding_verifier.py`](src/coding_verifier.py) currently checks:

- E/M assignments against structured MDM criteria using the 2-of-3 CMS framework
- High-yield CPT conflicts against an embedded subset of CMS Correct Coding Initiative edits
- ICD-10 specificity gaps, including unspecified codes when the transcript documents stage, linkage, or other added detail
- Common upcoding and downcoding patterns, especially unsupported high-level office visits

The runnable example in [`examples/coding_sample.json`](examples/coding_sample.json) shows the expected payload and audit output format, and [`scripts/coding_audit.py`](scripts/coding_audit.py) will emit the audit result as JSON for downstream review pipelines.

Typical workflow:

1. Generate transcript-derived codes with OpenEvidence Coding Intelligence.
2. Serialize the transcript, coding output, and structured clinical context into JSON.
3. Run `python scripts/coding_audit.py visit.json -o coding_audit.json`.
4. Review flagged E/M, CPT, and ICD-10 findings before final claim submission.

This is positioned for compliance auditing and QA. It does not replace certified coding review, payer-specific policy checks, or the full CMS CCI dataset.

---

## Rubric Scoring

The pipeline includes a multi-dimensional rubric that scores each citation across nine dimensions instead of assigning a single error category. This enables severity-weighted prioritization and before/after comparison when fixes are applied.

### Dimensions

| Dimension | Weight | Description |
|-----------|--------|-------------|
| doi_existence | 0.10 | Does the DOI resolve in CrossRef? |
| url_resolution | 0.10 | Does the URL return a valid page? |
| topic_alignment | 0.10 | Does the paper's topic match the claim's domain? |
| claim_support | 0.25 | Does the paper's conclusion support the specific claim? |
| statistic_accuracy | 0.15 | Do cited numbers appear in the source? |
| author_accuracy | 0.10 | Is the first author correct? |
| year_accuracy | 0.05 | Is the publication year correct? |
| journal_accuracy | 0.05 | Is the journal name correct? |
| direction_of_effect | 0.10 | Does the paper's finding direction match the framing? |

### Fix Validation

When an LLM corrects a citation, the rubric scores before and after. The fix is accepted only if the composite improvement exceeds a minimum delta (default: 0.15). This prevents "fixes" that introduce new errors or produce negligible improvement.

```python
from rubric import CitationRubric

rubric = CitationRubric()
before = rubric.score(result_before_fix)
after = rubric.score(result_after_fix)
delta = rubric.compare(before, after)

if delta.is_improvement(min_delta=0.15):
    print(f"Fix accepted: {delta.composite_delta:+.2f}")
else:
    print(f"Fix rejected: delta {delta.composite_delta:+.2f} below threshold")
```

### Custom Weights

Weights are configurable for different use cases. A clinical handbook might weight `statistic_accuracy` and `direction_of_effect` higher; a literature review might weight `author_accuracy` higher.

```python
from rubric import CitationRubric, Dimension

weights = {dim: 0.05 for dim in Dimension}
weights[Dimension.CLAIM_SUPPORT] = 0.40
weights[Dimension.STATISTIC_ACCURACY] = 0.20
# Weights must sum to 1.0

rubric = CitationRubric(weights=weights)
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
|   |-- rubric.py                   Multi-dimensional rubric scoring
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
