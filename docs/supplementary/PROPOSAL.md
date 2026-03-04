# Research Proposal: Comparative Citation Accuracy Across Medical LLM Systems

**Author:** Bryan Tegomoh, MD, MPH
**Date:** January 19, 2026
**Version:** 1.0

---

## Executive Summary

This proposal outlines a rigorous research methodology to compare citation accuracy across seven LLM systems generating medical content. Using the validated four-phase verification pipeline (extended to five phases with Phase 0), we will systematically evaluate which systems produce the most reliable citations and identify system-specific failure patterns.

---

## Research Questions

### Primary Question
Which LLM systems exhibit the lowest citation error rates when generating medical content with academic references?

### Secondary Questions
1. Do medical-specialized LLMs (OpenEvidence, Doximity GPT) outperform general-purpose LLMs?
2. Do search-augmented LLMs (Perplexity) have lower fabrication rates?
3. What error type distributions characterize each system?
4. Does query specificity (foundational vs. specialized) affect error rates differently across systems?
5. Are certain systems more prone to specific failure modes (e.g., wrong paper, fabricated DOI)?

---

## Target Systems

| System | Category | Access Method | Notes |
|--------|----------|---------------|-------|
| **OpenEvidence** | Medical-specialized | Web interface | Specifically designed for clinical decision support |
| **Doximity GPT** | Medical-specialized | Doximity platform | Physician-facing, medical context |
| **ChatGPT (GPT-4)** | General-purpose | API/Web | Most widely used general LLM |
| **Claude (Opus 4.5)** | General-purpose | API/Web | Strong reasoning capabilities |
| **Grok** | General-purpose | X platform | Real-time information access |
| **Gemini** | General-purpose | Google AI | Multimodal, integrated with search |
| **Perplexity** | Search-augmented | Web interface | Explicitly citation-focused |

### System Selection Rationale

1. **Medical-specialized (2):** Test whether domain-specific training improves citation accuracy
2. **General-purpose (4):** Baseline comparison across major commercial LLMs
3. **Search-augmented (1):** Test whether real-time search integration reduces fabrication

---

## Methodology

### Phase 1: Query Development

#### Query Categories (15 total queries)

**Category A: Foundational Questions (5 queries)**
Well-documented topics with extensive literature:

1. "What is the evidence base for AI in medical imaging? Provide specific studies with citations."
2. "What are the key validation studies for clinical decision support systems in hospitals? Include DOIs."
3. "How accurate are AI sepsis prediction models compared to traditional scores? Cite the evidence."
4. "What does the research show about algorithmic bias in healthcare AI? Provide peer-reviewed sources."
5. "What are the FDA-cleared AI medical devices and what evidence supports their approval?"

**Category B: Specialized Questions (5 queries)**
Domain-specific topics requiring specialized knowledge:

1. "What is the evidence for AI in fetal heart rate monitoring during labor? Provide citations."
2. "What studies have validated AI-assisted capsule endoscopy? Include specific accuracy metrics."
3. "How has AI performed in psychiatric risk prediction? Cite validation studies."
4. "What evidence exists for AI in predicting preterm birth? Provide DOIs."
5. "What studies have evaluated AI for detecting diabetic macular edema? Include sample sizes."

**Category C: Statistical Questions (5 queries)**
Requiring specific numerical claims:

1. "What sensitivity and specificity do AI chest X-ray models achieve for pneumonia detection? Cite sources."
2. "What are the reported accuracy rates for AI melanoma detection? Provide specific study results."
3. "What sample sizes have been used in the largest AI validation studies in healthcare? List studies."
4. "What AUC values have been reported for AI sepsis prediction? Cite the specific papers."
5. "What are the positive predictive values for AI-detected pulmonary nodules? Provide citations."

#### Query Standardization

All queries will:
- Request explicit citations/DOIs
- Avoid leading language about specific papers
- Use consistent formatting across systems
- Be executed in randomized order per system

### Phase 2: Response Collection

#### Protocol

1. **Timing:** All responses collected within a 48-hour window to minimize model updates
2. **Recording:** Full response text captured including all citations
3. **Metadata:** Timestamp, system version (if available), any error messages
4. **Format Normalization:** Convert all citations to standard format: `[Author et al., Year](URL)`

#### Quality Controls

- Each query executed once per system (no re-prompting for "better" citations)
- No follow-up queries to improve responses
- Raw responses archived before any processing

### Phase 3: Citation Extraction

#### Extraction Protocol

Use `citation_extractor.py` (modified) to extract:
- Citation text (author, year)
- URL/DOI
- Surrounding claim context (200 characters)
- System source identifier

#### Expected Yield

- 7 systems × 15 queries = 105 query-response pairs
- Estimated 5-10 citations per response
- Expected total: 500-1,000 citations for verification

### Phase 4: Verification Pipeline

Apply the five-phase verification pipeline to ALL extracted citations:

#### Phase 0: DOI Existence Validation (NEW)
```python
# For each DOI-format URL
result = crossref_api.check_existence(doi)
if not result.exists:
    flag_as("FABRICATED_DOI")
```

#### Phase 1: URL Resolution
```python
response = http_request(url)
if response.status == 404:
    flag_as("BROKEN_URL")
elif response.status == 200:
    proceed_to_phase_2()
```

#### Phase 2: Content-Claim Alignment
- Extract paper title, abstract, findings
- Compare to claim made in LLM response
- Classification: ALIGNED / PARTIAL / MISMATCH / WRONG_PAPER

#### Phase 3: Metadata Verification
- Verify first author
- Verify publication year
- Verify journal name
- Cross-reference with PubMed/CrossRef

#### Phase 4: Error Classification
Assign final error category:
- VERIFIED_CORRECT
- BROKEN_URL
- FABRICATED_DOI
- WRONG_PAPER
- CLAIM_MISMATCH
- AUTHOR_ERROR
- YEAR_ERROR
- JOURNAL_ERROR
- METRIC_ERROR
- FABRICATED_STATISTIC

### Phase 5: Statistical Analysis

#### Primary Metrics

| Metric | Formula |
|--------|---------|
| Total Error Rate | Errors / Total citations |
| Fabrication Rate | (Broken + Fabricated DOI) / Total |
| Content Match Rate | ALIGNED / (Total - Broken) |
| Specificity Accuracy | Correct statistics / Claimed statistics |

#### Comparisons

1. **Inter-system comparison:** Error rates across all 7 systems
2. **Category comparison:** Medical-specialized vs. general-purpose vs. search-augmented
3. **Query type comparison:** Foundational vs. specialized vs. statistical
4. **Error type distribution:** Which systems prone to which error types

#### Statistical Tests

- Chi-square for error rate differences between systems
- Fisher's exact test for rare error types
- Kruskal-Wallis for non-parametric multi-group comparisons
- Significance threshold: p < 0.05 with Bonferroni correction for multiple comparisons

---

## Blinding Protocol

To reduce verification bias:

1. **Extraction phase:** Citations pooled and shuffled before verification
2. **Verification phase:** Verifier does not know which system generated citation
3. **Classification phase:** Error category assigned before system revealed
4. **Unblinding:** Only after all 500-1,000 citations verified

---

## Expected Results

### Hypotheses

**H1:** Medical-specialized systems (OpenEvidence, Doximity GPT) will have lower error rates than general-purpose systems for medical content.

**H2:** Search-augmented systems (Perplexity) will have lower fabrication rates (broken URLs, fabricated DOIs) than systems without search integration.

**H3:** All systems will show higher error rates for statistical questions (Category C) than foundational questions (Category A).

**H4:** General-purpose systems will show higher error rates for specialized questions (Category B) than medical-specialized systems.

**H5:** Wrong paper errors (valid DOI, wrong content) will be more common than broken URL errors across all systems.

### Power Analysis

With 500-1,000 citations total and approximately 70-100 per system:
- Detectable difference in error rates: ~15-20% between systems
- 80% power at α = 0.05

---

## Timeline

| Week | Activity |
|------|----------|
| 1 | Finalize query set, pilot test on 2 systems |
| 2 | Collect responses from all 7 systems |
| 3-4 | Citation extraction and verification (Phase 0-3) |
| 5 | Error classification and quality assurance |
| 6 | Statistical analysis and figure generation |
| 7 | Manuscript drafting |
| 8 | Revision and submission |

---

## Deliverables

1. **Dataset:** Complete verification results for all citations (JSON format)
2. **Figures:**
   - Figure 1: Error rate comparison across systems (bar chart)
   - Figure 2: Error type distribution by system (stacked bar)
   - Figure 3: Error rates by query category (grouped bar)
   - Figure 4: Fabrication rates comparison (bar chart)
   - Figure 5: Heatmap of error types × systems
3. **Manuscript:** Publishable paper comparing LLM citation accuracy
4. **Supplementary Materials:** Full verification logs, query transcripts

---

## Ethical Considerations

### No Patient Data
This study uses only LLM-generated content and published literature. No patient data involved.

### Transparency
All query prompts and verification methodology will be published for reproducibility.

### Limitations Acknowledged
- Single time point (model versions may change)
- Specific query set (may not generalize to all medical queries)
- English-language sources only

---

## Alternative Research Designs

### Design 2: Longitudinal Tracking

Instead of comparing systems, track ONE system over time:
- Same 15 queries repeated monthly for 6 months
- Assess whether citation accuracy improves with model updates
- Pros: Controls for query variability
- Cons: Slower, less comparative insight

### Design 3: Prompt Engineering Impact

Compare citation accuracy with different prompt strategies:
- Baseline: "Cite sources"
- Enhanced: "Provide DOIs from peer-reviewed journals"
- Explicit: "Only cite papers you can verify exist"
- Pros: Actionable recommendations for users
- Cons: Doesn't compare fundamental system capabilities

### Design 4: Domain Expansion

Test same methodology across multiple domains:
- Medical (current proposal)
- Legal (case law citations)
- Scientific (chemistry, physics)
- Pros: Broader applicability
- Cons: Requires domain expertise for each area

---

## Recommendation

**Proceed with primary design (comparative cross-sectional study)** for the following reasons:

1. Answers the most pressing question: Which systems are most reliable?
2. Enables immediate practical recommendations
3. Generates publishable results within 8 weeks
4. Uses validated methodology from current work

Future work can incorporate longitudinal tracking (Design 2) and prompt engineering (Design 3) as follow-up studies.

---

## Budget and Resources

### Required
- Access to all 7 LLM systems (API costs for ChatGPT, Claude)
- Computation for verification scripts
- Human verification time (~40-60 hours)

### Estimated Costs
- API costs: $100-200
- Human time: 40-60 hours
- Total: Feasible for individual researcher

---

## References

1. Alkaissi H, McFarlane SI. Artificial hallucinations in ChatGPT: implications in scientific writing. Cureus. 2023;15(2):e35179.
2. Walters WH, Wilder EI. Fabrication and errors in the bibliographic citations generated by ChatGPT. Sci Rep. 2023;13(1):14045.
3. Thirunavukarasu AJ, et al. Large language models in medicine. Nat Med. 2023;29(8):1930-1940.

---

*Proposal Version: 1.0*
*Last Updated: January 19, 2026*
