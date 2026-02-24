# Citation Verification Toolkit

**Version:** 3.0
**Date:** January 29, 2026
**Purpose:** Detect and correct citation errors in LLM-generated content
**Domain:** Generalizable to any field with academic citations

---

## What This Toolkit Does

Large Language Models generate plausible-looking citations that are frequently wrong. This toolkit provides:

1. **A 5-phase verification pipeline** to systematically catch citation errors
2. **A 5-layer defense architecture** to prevent and detect errors at multiple points
3. **Python scripts** for automated verification
4. **Documentation** of methodology and findings

**Key finding:** Only 21% of citation errors are detectable by URL checking alone. The remaining 79% require content-level verification.

---

## Quick Start

### Installation

```bash
cd scripts
pip install -r requirements.txt
```

### Verify Citations in Your Documents

```bash
# Verify all markdown files in a directory
python verification_pipeline.py ./content/ -o report.json

# Include a human-readable report
python verification_pipeline.py ./content/ -o report.json --markdown

# Verify a single file
python verification_pipeline.py paper.md -o report.json
```

### Example Output

```
Starting verification pipeline for: ./content/
Phases to run: [0, 1, 2, 3]
--------------------------------------------------

[Extraction] Extracting citations...
  Total citations: 89
  Unique citations: 72
  Duplicates: 17

[Phase 0] Validating DOI existence...
  Fabricated DOIs: 3

[Phase 1] Verifying URLs...
  Broken URLs: 5

[Phase 2] Verifying content alignment...
  Wrong papers: 8
  Claim mismatches: 4

[Phase 3] Verifying metadata...
  Author errors: 6
  Year errors: 4

==================================================
VERIFICATION COMPLETE
==================================================
Total citations: 72
Verified correct: 42
Total errors: 30
Error rate: 41.7%
```

---

## The Five-Phase Pipeline

```
Phase 0: DOI Existence → Does this DOI exist in CrossRef?
         ↓
Phase 1: URL Resolution → Does the URL return 200 OK?
         ↓
Phase 2: Content Alignment → Does the paper support the claim?
         ↓
Phase 3: Metadata Accuracy → Are author/year/journal correct?
         ↓
Phase 4: Correction → What's the fix?
```

### Error Categories

| Error Type | Phase | Description |
|------------|-------|-------------|
| FABRICATED_DOI | 0 | DOI follows valid format but doesn't exist |
| BROKEN_URL | 1 | URL returns 404 or fails to resolve |
| WRONG_PAPER | 2 | Valid URL, completely different paper |
| CLAIM_MISMATCH | 2 | Paper exists but doesn't support claim |
| AUTHOR_ERROR | 3 | Wrong first author name |
| YEAR_ERROR | 3 | Wrong publication year |
| FABRICATED_STATISTIC | 0+2 | Specific numbers with no source |

---

## The Five-Layer Defense Architecture

For production use, implement verification at multiple layers:

```
Layer 1: BEHAVIORAL    - Rules at content generation time
Layer 2: REAL-TIME     - Checks after each edit
Layer 3: PRE-COMMIT    - Validation before committing changes
Layer 4: ON-DEMAND     - Deep verification when needed
Layer 5: REGISTRY      - Known-good citations whitelist
```

See `METHODOLOGY.md` Section 15 for implementation details.

---

## Files Included

### Documentation

| File | Description |
|------|-------------|
| `README.md` | Quick start guide (this file) |
| `METHODOLOGY.md` | Complete verification methodology |
| `PAPER.md` | Research manuscript for publication |

### Scripts

| Script | Purpose |
|--------|---------|
| `verification_pipeline.py` | Main tool - runs full pipeline |
| `citation_extractor.py` | Extract citations from markdown |
| `doi_validator.py` | Phase 0: CrossRef API validation |
| `url_verifier.py` | Phase 1: HTTP status checking |
| `content_verifier.py` | Phase 2: Content alignment |
| `metadata_verifier.py` | Phase 3: Author/year validation |
| `generate_figures.py` | Publication figures |

---

## Supported File Types

- `.md` (Markdown)
- `.qmd` (Quarto)
- `.rst` (reStructuredText)
- `.txt` (Plain text)

Citations must be in markdown link format:
```markdown
[Author et al., Year](https://doi.org/...)
[Author, Year](https://url)
```

---

## Domain Applicability

While developed for medical content, this toolkit works for any domain:

- **Medical/Scientific** - Journal articles, clinical studies
- **Legal** - Case law, statutes, regulations
- **Policy** - Government documents, reports
- **Technical** - Standards, specifications, RFCs

Only Phase 2 (content alignment) requires domain expertise.

---

## Limitations

1. **Phase 2 requires human judgment** - Content-claim alignment can't be fully automated
2. **Paywalled content** - Some papers may not be accessible
3. **Non-English sources** - Tested primarily with English citations
4. **API rate limits** - CrossRef API has rate limits

---

## Citation

If using this methodology in research:

```bibtex
@misc{tegomoh2026citation,
  title={Five-Phase Citation Verification Pipeline for LLM-Generated Content},
  author={Tegomoh, Bryan},
  year={2026},
  url={https://github.com/BryanTegomoh/citation-hallucination-audit}
}
```

---

## License

MIT License - Free for academic and commercial use.

---

*Version 3.0 - Last Updated: January 29, 2026*
