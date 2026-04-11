# Citation Verification Toolkit

**Purpose:** Detect and correct citation errors in medical and scientific content.
**Author:** Bryan Tegomoh, MD, MPH
**License:** MIT

---

## The Problem

Citations that look correct frequently are not. Standard verification (checking whether a URL resolves) catches approximately 21% of errors. The remaining 79% require reading the cited paper and confirming it supports the specific claim. This finding is consistent with SourceCheckup (Nature Communications 2025), which found 50-90% of LLM-generated medical citations are not fully supported by their sources.

This toolkit implements a five-phase verification pipeline with 42 documented failure modes across six categories, covering everything from fabricated DOIs to scope extrapolation, retracted paper citation, and evidence strength inflation.

It can also audit AI-generated medical coding output by checking whether suggested E/M, CPT, and ICD-10 codes are supported by the clinical transcript and structured documentation.

---

## The Five-Phase Pipeline

```
Phase 0: DOI Existence        CrossRef registry lookup
         |
Phase 1: URL Resolution       HTTP status + redirect chain analysis
         |
Phase 2: Content Alignment    Semantic verification against source text
         |    + Semantic       Scope, causality, evidence strength, direction
         |
Phase 3: Metadata Accuracy    Author, year, journal, retraction, funding
         |
Phase 4: Correction           Fix identification and replacement search
```

### Error Taxonomy (42 Failure Modes)

**Phase 0-1: Structural**

| Error Type | Description |
|------------|-------------|
| FABRICATED_DOI | DOI follows valid format but does not exist in CrossRef |
| BROKEN_URL | URL returns 404 or fails to resolve |
| FABRICATED_REPOSITORY | Plausible GitHub/GitLab URL that does not exist |
| GENERIC_URL | URL resolves to homepage, not specific cited document |
| FABRICATED | Paper, authors, and journal do not exist |

**Phase 2: Content Alignment**

| Error Type | Description |
|------------|-------------|
| WRONG_PAPER | Valid URL, completely different paper |
| CLAIM_MISMATCH | Paper exists but does not support specific claim |
| CITATION_OVERLOADING | Single citation used for claims from multiple papers |
| STATISTIC_CONFLATION | Multiple study periods collapsed into one figure |
| METRIC_ERROR | Specific numbers (percentages, sample sizes) are wrong |
| FABRICATED_STATISTIC | Numbers cited without verifiable source |
| INVERTED_STATISTICS | Correct numbers assigned to wrong labels |
| CHIMERA_CITATION | Real components assembled into fabricated paper |

**Phase 2: Semantic Misrepresentation**

| Error Type | Description |
|------------|-------------|
| SCOPE_EXTRAPOLATION | Narrow study cited as broad evidence |
| EVIDENCE_STRENGTH_INFLATION | Pilot data cited as "demonstrated" |
| CAUSAL_INFERENCE_ESCALATION | Correlation cited as causation |
| PARTIAL_SUPPORT | Paper partially supports claim (not fully) |
| DRUG_NAME_SUBSTITUTION | Phonetically similar but different drug |
| GEOGRAPHIC_POPULATION_MISMATCH | Single-country study cited as global evidence |
| CONFERENCE_ABSTRACT_AS_PAPER | Preliminary abstract cited as full paper |
| EFFECT_SIZE_DIRECTION_REVERSAL | Positive finding cited as negative (or vice versa) |
| DENOMINATOR_SHIFT | Citation changes denominator, altering mathematical meaning |
| DRAWBACK_OMISSION | Balanced paper presented as one-sided |
| QUALIFIER_OMISSION | Paper says "rare"; response drops qualifier |
| INTERVENTION_MISCHARACTERIZATION | Finding from Study A attributed to Study B |
| INTERVENTION_MISATTRIBUTION | Correct figure attributed to wrong mechanism |
| CONFLATION_ACROSS_STUDIES | Two distinct interventions merged into one |
| DECORATION_CITATION | Citation appears but adds no evidentiary value |
| SECONDARY_SOURCE_OVERRELIANCE | Grand Rounds cited when original guideline should be |
| AMBIGUITY | Phrasing creates confusion between distinct concepts |

**Phase 3: Metadata**

| Error Type | Description |
|------------|-------------|
| AUTHOR_ERROR | Wrong first author name |
| YEAR_ERROR | Wrong publication year |
| JOURNAL_ERROR | Correct paper, wrong journal name |
| SAMPLE_SIZE_FABRICATION | Plausible sample size that does not match study |

**Source Selection**

| Error Type | Description |
|------------|-------------|
| RETRACTED_PAPER | Paper has been formally retracted |
| SUPERSEDED_EVIDENCE | Guideline replaced by newer version |
| POPULARITY_BIAS | Most-cited paper selected over most-relevant |

**Systemic**

| Error Type | Description |
|------------|-------------|
| POST_RATIONALIZATION | Correct citation retrofitted after generation |
| PREDATORY_JOURNAL | Paper from predatory/low-quality venue |
| TRAINING_DATA_CONTAMINATION | Fabricated citation entered published literature |
| GHOST_REFERENCE | Secondary citations create false verification loop |
| CONFLICT_OF_INTEREST_BLINDNESS | Industry-funded study cited without disclosure |

---

## Quick Start

```bash
pip install -r requirements.txt

# Full pipeline (all phases)
python scripts/verification_pipeline.py ./content/ -o report.json

# With human-readable report
python scripts/verification_pipeline.py ./content/ -o report.json --markdown

# Verify with rubric scoring (JSON + markdown rubric reports)
python scripts/verification_pipeline.py ./content/ -o report.json --rubric

# Specific phases only
python scripts/verification_pipeline.py ./content/ --phases 0 1

# Verify a single file
python scripts/verification_pipeline.py paper.md -o report.json

# Semantic verification (scope, causality, retraction)
python scripts/semantic_verifier.py content_verification.json -o semantic_report.json

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
|   |-- verification_pipeline.py    Main orchestrator (all phases)
|   |-- citation_extractor.py       Extract citations from markdown
|   |-- doi_validator.py            Phase 0: CrossRef API validation
|   |-- url_verifier.py             Phase 1: HTTP status checking
|   |-- content_verifier.py         Phase 2: Content-claim alignment
|   |-- semantic_verifier.py        Phase 2+: Semantic verification
|   |-- metadata_verifier.py        Phase 3: Metadata + retraction
|   |-- rubric.py                   Multi-dimensional rubric scoring
|
|-- src/                      Installable Python package
|   |-- extractors/                 BibTeX, markdown, plaintext parsers
|   |-- validators/                 CrossRef, DOI resolver, prefix checker
|   |-- reporters/                  Markdown report generation
|
|-- data/                     Reference data
|   |-- publisher_prefixes.json     DOI prefix-to-publisher mapping (90+)
|   |-- journal_patterns.json       Journal name patterns
|
|-- docs/                     Documentation
|   |-- METHODOLOGY.md              Full methodology (42 failure modes)
|   |-- hallucination-patterns.md   Pattern catalog with examples
|   |-- verification-workflow.md    Decision tree for verification
|   |-- case-studies.md             Real-world audit examples
|
|-- papers/                   Research manuscripts
|-- reports/                  Audit reports
|-- examples/                 Sample files and reports
|-- tests/                    Test suite
```

---

## Key Findings

From verification of 838 citations across 22 medical specialty chapters:

- 21% of citation errors are URL-detectable (broken links, failed DOIs)
- 79% require content-level verification (Phase 2+)
- 64% of fabricated DOIs resolve to real but unrelated papers
- Fabrication rates range from 6% (well-studied topics) to 29% (niche topics)
- 42 distinct failure modes documented across 6 categories

These findings align with SourceCheckup (Nature Communications 2025), which found 50-90% of LLM medical citations are not fully supported by their sources, and the GPTZero NeurIPS analysis, which found 100+ hallucinated citations surviving peer review.

---

## Semantic Verification Module

The `semantic_verifier.py` module detects higher-order failures invisible to URL checking:

| Check | What It Detects |
|-------|-----------------|
| `RetractionChecker` | Papers retracted after publication |
| `StudyDesignClassifier` | Study design (RCT, cohort, case report, etc.) |
| `CausalLanguageDetector` | Causal claims from observational studies |
| `ScopeAnalyzer` | Narrow studies cited as broad evidence |
| `DirectionOfEffectChecker` | Positive findings cited as negative |
| `ConferenceAbstractDetector` | Abstracts cited as full papers |
| `DrugNameChecker` | Phonetic drug name substitutions |
| `FundingAnalyzer` | Industry funding and COI flags |

---

## Limitations

1. Phase 2 (content-claim alignment) requires domain expertise for final judgment
2. Paywalled content limits automated full-text verification
3. Retraction database coverage depends on CrossRef metadata completeness
4. Tested primarily with English-language citations
5. CrossRef API has rate limits for high-volume verification
6. Semantic checks (scope, causality) are heuristic, not deterministic

---

## Related Work

| Tool / Paper | Focus | Relationship |
|-------------|-------|-------------|
| SourceCheckup (Nature Communications 2025) | 50-90% non-support rate | Validates the 79% content-level finding |
| BibAgent (arXiv 2601.16993) | 5-dimension miscitation taxonomy | This toolkit extends with medical-specific modes |
| SemanticCite (arXiv 2511.16198) | 4-class support taxonomy | Adopted in content_verifier.py |
| GhostCite (arXiv 2602.06718) | 2.2M citations, 14-94% hallucination | Prevalence data for error taxonomy |
| CheckIfExist (arXiv 2602.15871) | Multi-source DOI validation | Complementary to Phase 0 |
| DriftMedQA (arXiv 2505.07968) | Guideline supersession detection | Informs Gap 23 |

---

## Citation

```bibtex
@misc{tegomoh2026citation,
  title={Five-Phase Citation Verification Pipeline for AI-Generated Medical Text},
  author={Tegomoh, Bryan},
  year={2026},
  url={https://github.com/BryanTegomoh/citation-audit}
}
```

---

## License

MIT License. Free for academic and commercial use.
