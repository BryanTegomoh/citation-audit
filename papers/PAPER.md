# A Five-Phase Pipeline and Five-Layer Defense Architecture for Detecting and Correcting Citation Errors in Large Language Model-Generated Content

**Authors:** Bryan Tegomoh, MD, MPH

**Corresponding Author:** Bryan Tegomoh, bryantegomoh.com

**Word Count:** 10,500 (excluding references and supplementary materials)

**Version:** 3.3 (February 24, 2026)

---

## Abstract

**Background:** Large language models (LLMs) are increasingly used to generate academic and scientific content, but their tendency to produce plausible-sounding but erroneous citations poses significant risks to scientific integrity. Current automated verification tools detect only URL-level failures, missing the majority of citation errors including fabricated DOIs, wrong papers, claim-citation mismatches, and metadata inaccuracies.

**Objective:** To develop and validate a systematic methodology for comprehensive citation verification in LLM-generated content that addresses the full spectrum of citation error types, and to propose a defense-in-depth architecture for preventing and detecting errors at multiple points in the content lifecycle.

**Methods:** We developed a five-phase verification pipeline: (0) DOI existence validation via CrossRef API, (1) URL/DOI resolution testing, (2) content-claim alignment verification, (3) metadata accuracy verification, and (4) correction and replacement. We additionally developed a five-layer defense architecture implementing verification at behavioral, real-time, pre-commit, on-demand, and registry layers. The methodology was iteratively refined through application to LLM-generated content and implemented as automated tooling.

**Results:** In validation testing, approximately 47% of LLM-generated citations contained errors. Error distribution: wrong paper with valid DOI (25.7%), broken DOI/URL (21.4%), year errors (12.9%), author attribution errors (11.4%), claim-citation mismatches (10.0%), journal misattribution (10.0%), and metric errors (8.6%). Notably, only 21.4% of errors would be detected by automated link-checking tools. The remaining 78.6% required content-level verification to identify. Fabricated citations with syntactically valid but non-existent DOIs represent a particularly insidious failure mode, detectable only through Phase 0 DOI registry queries.

**Conclusions:** LLM-generated citations exhibit high error rates with the majority undetectable by automated tools. Our five-phase pipeline provides a reproducible methodology for comprehensive citation verification, while our five-layer defense architecture provides defense-in-depth for production content systems. The methodology is generalizable across domains and LLM systems. We recommend mandatory citation verification for all LLM-assisted academic content, with verification integrated into authoring workflows rather than applied only post-hoc.

**Keywords:** Large language models, citation verification, hallucination, scientific writing, scientific integrity, artificial intelligence, defense-in-depth, DOI validation, CrossRef

---

## 1. Introduction

### 1.1 The Rise of LLM-Assisted Content Generation

Large language models (LLMs) have rapidly transformed content generation across domains, including medical and scientific writing. Models such as GPT-4, Claude, and Gemini can produce sophisticated technical prose that appears authoritative and well-referenced. Healthcare institutions, medical educators, and researchers increasingly use these tools to draft clinical documentation, educational materials, and even research manuscripts.

However, a critical limitation of LLMs is their tendency to generate "hallucinations"—content that appears plausible but is factually incorrect. In the context of academic citations, this manifests as references that look legitimate but suffer from various forms of error, from broken URLs to entirely fabricated papers.

### 1.2 The Citation Hallucination Problem

Citation hallucination in LLMs presents unique challenges distinct from other forms of AI-generated misinformation:

1. **Format Plausibility:** LLMs generate citations in correct academic format (author, year, journal, DOI) that pass superficial inspection
2. **Partial Accuracy:** Many erroneous citations contain partially correct information (real authors, real journals) mixed with fabricated elements
3. **Semantic Drift:** Citations may reference real papers that are topically related but do not support the specific claim made
4. **Compound Errors:** A single citation may contain multiple error types (wrong author AND wrong year AND wrong DOI)

Previous research has documented LLM citation hallucination rates ranging from 30% to over 70% depending on the model and domain. However, most studies focus on binary classification (exists/does not exist) rather than the nuanced error taxonomy we propose here.

### 1.3 Limitations of Current Verification Approaches

Existing citation verification tools fall into several categories, each with significant limitations:

**Automated Link Checkers:** Tools that verify URL/DOI resolution detect only broken links, missing the majority of errors where valid URLs point to wrong or mismatched content.

**Reference Management Software:** Tools like EndNote, Zotero, and Mendeley verify format consistency but do not assess whether cited content supports inline claims.

**Plagiarism Detection:** Software like Turnitin identifies copied text but does not verify citation accuracy or claim-citation alignment.

**Manual Peer Review:** Traditional peer review may catch obvious errors but lacks systematic methodology and often trusts author-provided citations without verification.

### 1.4 The Need for Systematic Verification Methodology

The gap between current verification capabilities and the complexity of LLM citation errors necessitates a new approach. An effective methodology must:

1. Detect URL-level failures (broken links, 404 errors)
2. Verify that resolved URLs point to the claimed paper
3. Confirm that paper content supports the inline claim
4. Validate metadata accuracy (author, year, journal)
5. Identify fabricated citations that leave no trace

This paper presents such a methodology, validated through application to a substantial medical text corpus.

### 1.5 Research Questions

**Primary Research Question:** What is the prevalence and distribution of citation error types in LLM-assisted medical text generation?

**Secondary Research Questions:**
1. What proportion of citation errors are detectable by automated link-checking tools versus requiring content-level verification?
2. Can a systematic verification pipeline be developed that is reproducible and scalable?
3. What error taxonomy best characterizes the failure modes of LLM-generated citations?

---

## 2. Methods

### 2.1 Study Design

We conducted a systematic verification study of all citations in a 22-chapter medical AI handbook. The handbook was produced using LLM assistance for initial drafting, with human expert review and editing. This represents a realistic use case for LLM-assisted medical content generation.

### 2.2 Corpus Description and Applicability

The methodology is designed to be applied to any corpus of LLM-generated medical or scientific text. For validation, we recommend testing corpora that:

1. **Contain diverse citation types**: DOI links, PubMed URLs, journal websites
2. **Span multiple topics**: Different medical specialties or scientific domains
3. **Include varying claim specificity**: Both general statements and specific statistics
4. **Represent realistic LLM use cases**: Draft documents, research summaries, educational content

**Recommended Test Corpus Structure:**
- Foundational content (history, fundamentals, methodology)
- Applied/specialty content (specific domains requiring specialized citations)
- Mixed-specificity claims (general statements and precise metrics)

**Citation Format Targeted:** Inline hyperlinked citations in format: `([Author et al., Year](URL))`

This format is common across academic writing tools, LLM-assisted drafting, and modern digital publications.

### 2.3 Citation Extraction

Citations were extracted using regular expression pattern matching:

```
Pattern: \[([^\]]+)\]\((https?://[^\)]+)\)
```

This pattern captures:
- Group 1: Citation text (e.g., "Wong et al., 2021")
- Group 2: URL (e.g., "https://doi.org/10.1001/jamainternmed.2021.2626")

**Extraction Results:**
- Total citations extracted: 162
- Unique citations (deduplicated): 150
- Citations appearing in multiple chapters: 12

### 2.4 Five-Phase Verification Pipeline

The pipeline is structured to detect errors in order of severity, with fabricated DOIs caught earliest:

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

#### Phase 0: DOI Existence Validation (NEW)

**Objective:** Detect fabricated DOIs before wasting resources on URL resolution.

**Method:**
- Query CrossRef API: `https://api.crossref.org/works/{DOI}`
- Parse response for existence confirmation
- Extract authoritative metadata if DOI exists

**Classification:**
- DOI exists in CrossRef → Proceed to Phase 1
- DOI not found → Flag as FABRICATED_DOI

**Rationale:** LLMs generate syntactically valid DOIs (e.g., `10.1001/jamanetworkopen.2019.XXXXX`) that follow correct publisher patterns but do not exist in any registry. Standard URL verification returns 404, categorizing these as "broken links." Phase 0 distinguishes intentional fabrication from transcription errors.

**Tools Used:** CrossRef REST API with rate limiting

#### Phase 1: URL/DOI Resolution Testing

**Objective:** Verify that each URL resolves to an accessible resource.

**Method:**
- HTTP HEAD/GET request to each URL
- Follow redirects (301, 302) to final destination
- Record HTTP status codes
- For DOIs that passed Phase 0, verify resolution through doi.org

**Classification:**
- HTTP 200: Resolved successfully → Proceed to Phase 2
- HTTP 404: Broken URL → Flag for replacement
- HTTP 403: Access restricted → Attempt alternative access
- HTTP 3xx: Follow redirect chain, verify final destination

**Tools Used:** Web fetch capabilities with redirect following

#### Phase 2: Content-Claim Alignment Verification

**Objective:** Verify that cited paper content supports the inline claim.

**Method:**
1. Extract inline claim (200 characters surrounding citation)
2. Identify specific assertions:
   - Statistics (percentages, p-values, sample sizes)
   - Findings ("showed," "demonstrated," "found")
   - Conclusions ("therefore," "indicating")
3. Retrieve paper content (abstract, full text where available)
4. Compare claimed findings to actual paper content

**Classification:**
- Full Match: Paper directly supports claim
- Partial Match: Paper supports claim with minor discrepancy
- Mismatch: Paper does not support specific claim
- Wrong Paper: Paper topic entirely different from claim

#### Phase 3: Metadata Accuracy Verification

**Objective:** Verify citation metadata accuracy.

**Elements Verified:**
- First author surname
- Publication year
- Journal name
- DOI format validity

**Method:**
1. Extract metadata from landing page
2. Cross-reference with PubMed/academic databases
3. Verify DOI resolves to same paper as URL
4. Compare extracted metadata to citation text

#### Phase 4: Correction and Replacement

**Objective:** For each identified error, implement appropriate correction.

**Decision Algorithm:**

```
IF error_type == "broken_url":
    search_for_correct_doi()
    IF found: replace_url()
    ELSE: remove_citation_with_disclaimer()

IF error_type == "wrong_paper":
    search_for_paper_matching_claim()
    IF found: replace_citation()
    ELSE: rephrase_claim_to_match_available_evidence()

IF error_type == "claim_mismatch":
    EITHER find_supporting_citation()
    OR rephrase_claim_to_match_paper()

IF error_type == "metadata_error":
    correct_metadata_in_citation_text()

IF error_type == "fabricated":
    remove_claim_entirely()
    OR replace_with_general_statement_without_citation()
```

### 2.5 Error Taxonomy

Based on iterative refinement, we developed a comprehensive error taxonomy with detection phases:

| Category | Definition | Detection Phase |
|----------|------------|-----------------|
| **FABRICATED_DOI** | DOI follows valid format but doesn't exist in CrossRef | Phase 0 |
| **BROKEN_URL** | URL returns 404 or fails to resolve | Phase 1 |
| **WRONG_PAPER** | Valid URL points to unrelated paper | Phase 2 |
| **CLAIM_MISMATCH** | Paper exists but doesn't support inline claim | Phase 2 |
| **METRIC_ERROR** | Specific numbers (statistics) incorrect | Phase 2 |
| **AUTHOR_ERROR** | Wrong first author attribution | Phase 3 |
| **YEAR_ERROR** | Wrong publication year | Phase 3 |
| **JOURNAL_ERROR** | Wrong journal attribution | Phase 3 |
| **FABRICATED_STATISTIC** | Specific numbers have no verifiable source | Phase 0 + Phase 2 |
| **INVERTED_STATISTICS** | Correct numbers assigned to wrong metric labels | Phase 2 (enhanced) |
| **FABRICATED_REPOSITORY** | Code repository URL (e.g., GitHub) that does not exist | Phase 1 + Phase 2 |
| **GENERIC_URL** | URL resolves to homepage/landing page, not the specific document cited | Phase 2 |
| **CHIMERA_CITATION** | Real author + real statistics harvested from Paper A, assembled into non-existent Paper B with fabricated elaborations | Phase 2 + Phase 3 |
| **BOT_BLOCKED_URL** | Government/regulatory URL returns 403/404 to automated requests but is accessible in browsers | Phase 1 (false positive) |
| **FINDING_MISREPRESENTATION** | Correct paper, correct topic, but qualitative finding (direction of effect) is wrong | Phase 2 (enhanced) |
| **TRIAL_IDENTITY_CONFUSION** | Distinct studies by same author conflated; statistics from Study A attributed to Study B | Phase 2 + Phase 3 |

**Key Insight:** FABRICATED_DOI errors (Phase 0) are distinct from BROKEN_URL errors (Phase 1). A fabricated DOI indicates intentional hallucination by the LLM, while a broken URL may indicate link rot or transcription error. This distinction matters for understanding LLM failure modes and developing mitigations.

**Extended Insight (February 2026):** Three additional error categories were identified during cross-corpus validation (see Section 3.9). INVERTED_STATISTICS is particularly dangerous because the numbers themselves appear in the source paper, and both the citation and paper are topically aligned. Only line-by-line comparison of specific metric labels to their values reveals the error. Standard keyword or string-matching approaches pass these errors as "verified." FABRICATED_REPOSITORY errors represent a distinct failure mode where LLMs generate plausible GitHub URLs for tools or frameworks that do not exist; these require repository-specific existence checks separate from academic URL verification. GENERIC_URL errors occur when a citation appears to resolve successfully (HTTP 200) but the destination is a top-level page rather than the specific document referenced in the citation text.

**Extended Insight (February 2026, Cross-Corpus Update):** CHIMERA_CITATION represents the most sophisticated LLM fabrication pattern identified to date. Unlike FABRICATED_DOI (entirely invented) or WRONG_PAPER (real paper, wrong claim), a chimera combines verified components from a real paper (author name, specific statistics, institutional affiliation) with a fabricated publication venue, DOI, and elaborated findings that do not exist in the source. Because individual verification checks (author exists? statistics appear in literature? institution is real?) all pass, chimeras evade single-factor verification. Detection requires cross-referencing the specific DOI against the specific author AND verifying the claimed venue matches the actual publication venue for that work.

### 2.6 Five-Layer Defense Architecture

Beyond the verification pipeline, we developed a defense-in-depth architecture for production content systems. This recognizes that post-hoc verification alone is insufficient; verification must be integrated throughout the content lifecycle.

```
┌─────────────────────────────────────────────────────────────┐
│              FIVE-LAYER DEFENSE ARCHITECTURE                │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Layer 1: BEHAVIORAL (Prevention)                          │
│  ├─ Generation-time rules                                  │
│  ├─ Protocol: "Never construct URLs from memory"           │
│  └─ Effect: Reduces fabrication at source                  │
│                                                             │
│  Layer 2: REAL-TIME (Immediate Detection)                  │
│  ├─ Post-edit hooks                                        │
│  ├─ Triggered: After every file modification               │
│  └─ Effect: Catches errors within seconds of creation      │
│                                                             │
│  Layer 3: PRE-COMMIT (Batch Validation)                    │
│  ├─ Git pre-commit hooks                                   │
│  ├─ Triggered: Before version control commit               │
│  └─ Effect: Prevents bad citations from entering repo      │
│                                                             │
│  Layer 4: ON-DEMAND (Deep Verification)                    │
│  ├─ Manual invocation for comprehensive checks             │
│  ├─ Triggered: User request or scheduled                   │
│  └─ Effect: Full Phase 0-4 pipeline with human review      │
│                                                             │
│  Layer 5: REGISTRY (Known-Good Whitelist)                  │
│  ├─ Verified citations database                            │
│  ├─ Effect: Skip re-verification for confirmed citations   │
│  └─ Bonus: Audit trail of corrections                      │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

#### Layer Implementation Details

**Layer 1 (Behavioral):** Implemented as authoring guidelines (e.g., CLAUDE.md protocol) that instruct LLMs to verify citations during generation rather than fabricating from training data. Key rules include:
- Never construct URLs from memory
- WebSearch to verify source exists before citing
- Include DOI with every citation

**Layer 2 (Real-Time):** Implemented as PostToolUse hooks that trigger after every file edit. The hook extracts new citations from the diff and runs lightweight verification (DOI format validation, URL pattern checking). Citations flagged for deeper review are logged.

**Layer 3 (Pre-Commit):** Git pre-commit hooks run validation scripts before allowing commits. This catches errors that slip through Layer 2 and ensures the repository never contains unverified citations.

**Layer 4 (On-Demand):** Full five-phase verification pipeline invoked manually or on schedule. This is the comprehensive verification described in Section 2.4, including human review of content-claim alignment.

**Layer 5 (Registry):** A JSON database of verified citations with their verification status and timestamps. Citations in the registry can skip re-verification, reducing overhead. The registry also tracks historical errors as training data for future prevention.

#### Defense-in-Depth Rationale

No single layer catches all errors:
- Layer 1 reduces but cannot eliminate fabrication
- Layer 2 catches obvious errors but lacks deep verification
- Layer 3 enforces standards but runs only at commit time
- Layer 4 is comprehensive but expensive to run frequently
- Layer 5 accelerates verification but requires initial population

The combination provides overlapping coverage where each layer compensates for gaps in others.

### 2.7 Extended Failure Modes (Critical Gaps)

Through iterative application of the methodology, we identified nine critical failure modes that extend beyond traditional verification approaches. These gaps represent errors that can slip through standard verification pipelines:

#### Gap 1: Syntactically Valid but Non-Existent DOIs

**Pattern:** DOI follows correct publisher format (e.g., `10.1001/jamanetworkopen.2019.XXXXX`) but does not exist in the DOI registry.

**Why it's missed:** Standard URL verification returns 404, categorizing as "broken link." However, the DOI's syntactic validity suggests intentional fabrication rather than transcription error. The distinction matters for understanding LLM failure modes.

**Detection Enhancement:** Query CrossRef API for DOI existence BEFORE URL resolution. Non-existent DOIs with valid syntax should be flagged as "FABRICATED_DOI_PATTERN."

#### Gap 2: Claim Specificity Without Source

**Pattern:** Highly specific claims (exact percentages, specific institutions, precise sample sizes) that have no verifiable source.

**Example:** "35% reduction in cardiac arrests at University of Michigan" with a DOI that doesn't exist.

**Why it's missed:** When the URL fails (404), the claim itself is not flagged. The methodology catches the broken URL but doesn't explicitly note that the underlying statistic may be entirely fabricated.

**Detection Enhancement:** When Phase 1 fails on a citation supporting a specific statistic, flag as "UNVERIFIED_STATISTIC_CLAIM" requiring either: (a) finding alternative source, or (b) removing the specific claim.

#### Gap 3: Pre-Generation Verification Gap

**Pattern:** Citations are only verified post-hoc, after LLM-generated content exists.

**Why it's missed:** The fundamental root cause is that verification doesn't occur during content generation. LLMs can generate hundreds of citations before any verification runs.

**Detection Enhancement:** Integration guidance for real-time verification during LLM-assisted authoring. Each citation should be verified at generation time, not batch-processed afterward.

#### Gap 4: Paywalled Content Extraction Failure

**Pattern:** URL resolves (HTTP 200) but content extraction fails due to paywall, JavaScript rendering, or bot blocking.

**Why it's missed:** These citations are categorized as "UNABLE_TO_VERIFY" and may be deprioritized for human review. However, some represent genuine wrong-paper errors that simply couldn't be detected automatically.

**Detection Enhancement:**
- Track "unable to verify" citations separately
- Require manual sampling (e.g., 20% of "unable to verify" citations)
- Escalate if sampling reveals high error rate in this category

#### Gap 5: Cross-File Synchronization

**Pattern:** Same erroneous citation appears in multiple files/chapters. Correction in one location doesn't automatically propagate.

**Why it's missed:** The pipeline processes files independently. Deduplication occurs during extraction but correction tracking doesn't ensure cross-file consistency.

**Detection Enhancement:** Post-correction grep-based verification across all files. After every Edit, run:
```bash
grep -r "OLD_DOI_PATTERN" --include="*.md" --include="*.qmd"
```

#### Gap 6: Confidence Calibration

**Pattern:** Content alignment confidence scores (0.0-1.0) are not calibrated against actual error rates.

**Why it's missed:** A 0.6 confidence "ALIGNED" assessment may still represent an error. Without calibration, triage thresholds are arbitrary.

**Detection Enhancement:** Track confidence scores against ground truth verification outcomes. Establish empirical thresholds for human review escalation.

#### Gap 7: Fabricated Experiential Claims

**Pattern:** Anecdotal claims ("At University X, researchers found...") that aren't citation errors but content fabrication.

**Why it's missed:** These aren't citation errors per se but fabricated claims disguised as institutional experiences. The methodology focuses on citation verification, not claim verification without citations.

**Detection Enhancement:** Flag uncited institutional claims or practitioner anecdotes for verification. These patterns often accompany fabricated citations.

#### Gap 8: Scaling Human Review

**Pattern:** Phase 2 (content-claim alignment) requires human judgment. With high error rates, this creates a bottleneck.

**Why it's missed:** The methodology assumes human reviewer availability. At scale (1,000+ citations), this becomes impractical.

**Detection Enhancement:**
- Stratified sampling based on claim specificity risk
- Prioritize high-specificity claims (exact statistics, institutional attributions)
- Confidence-based triage: only escalate citations below threshold

#### Gap 9: DOI Existence Validation Timing

**Pattern:** Metadata verification (Phase 3) queries CrossRef/PubMed but only AFTER Phase 1 passes.

**Why it's missed:** Phase 1 treats all 404 errors equally. A non-existent DOI that follows correct format should trigger immediate fabrication detection, not just "broken URL" categorization.

**Detection Enhancement:** Reorder pipeline to query DOI registry before URL fetch:
```
Phase 0: DOI existence check (CrossRef API)
Phase 1: URL resolution (for DOIs that exist)
Phase 2-4: Continue as before
```

#### Gap 10: Cross-File Attribution Inconsistency

**Pattern:** The same fact, quote, or institutional claim is attributed to different people across different files. Each citation passes verification independently, but the cross-file inconsistency reveals at least one attribution is wrong.

**Example (discovered February 5, 2026):** An AMA statement about AI prescribing was attributed to "Dr. Bobby Mukkamala, AMA Board Chair" in one chapter but to "AMA CEO Dr. John Whyte" in another. Investigation revealed John Whyte became AMA CEO in July 2025, making the Mukkamala attribution stale.

**Why it's missed:** The verification pipeline processes files independently. Each citation resolves and matches its local context. Only cross-file comparison reveals the inconsistency.

**Detection Enhancement:** After completing per-file verification, run cross-file attribution comparison:
```bash
# Extract all attributed quotes and institutional claims
grep -rn "AMA\|CEO\|Board Chair\|Director" --include="*.md" --include="*.qmd" | sort
```
Group by topic and verify consistent attribution across files.

#### Gap 11: Post-Verification Regression

**Pattern:** A previously verified and corrected citation is re-broken by a subsequent editing session. The correction log shows the fix was applied, but a later edit introduced a new error at the same location.

**Example (discovered February 5, 2026):** On January 18, the verification correctly changed author attribution from "Arnal et al." to "Botta et al." in a critical care chapter. However, the replacement DOI suffix (`1953979`) was itself incorrect (returns 404). The correct suffix is `1933450`. The first fix was partially correct (right author, wrong DOI).

**Why it's missed:** Once a citation appears in the correction log as "fixed," it is assumed correct and skipped in future verification passes. The registry may mark it as verified based on the correction date, not re-verification.

**Detection Enhancement:**
1. After applying corrections, re-verify the corrected citation through Phase 0-1 (DOI existence + URL resolution) immediately
2. Flag citations that were corrected in previous sessions for mandatory re-verification
3. Track "correction lineage": if a citation was corrected once, it has higher regression risk

#### Gap 12: Journal-Publisher Mismatch (Institutional Context Swap)

**Pattern:** The DOI prefix identifies one publisher, but the citation text claims a different journal from a different publisher. This often occurs when the LLM confuses the institution where research was conducted with the journal where it was published, or mixes up journals from different publishers covering similar topics.

**Example (discovered February 5, 2026):**
- Galloway et al. 2019: Cited as Mayo Clinic Proceedings (`10.1016/j.mayocp...`, Elsevier prefix) but actually published in JAMA Cardiology (`10.1001/jamacardio...`, AMA prefix). The research may have involved Mayo Clinic, but the publication was in JAMA Cardiology.
- Freeman et al. 2020: Cited with a JAMA Dermatology DOI (`10.1001/jamadermatol...`) but actually published in BMJ (`10.1136/bmj.m127`).

**Why it's missed:** Standard Phase 1 checks only test whether the URL resolves. If the wrong DOI happens to point to a real paper (Pattern 1: Valid DOI, Wrong Paper), the error passes Phase 1. Phase 3 metadata checks compare author and year but may not systematically verify DOI prefix-to-journal alignment.

**Detection Enhancement:** Add a DOI prefix validation step between Phase 0 and Phase 1:
```python
PUBLISHER_PREFIXES = {
    "10.1001": "JAMA Network (AMA)",
    "10.1016": "Elsevier",
    "10.1038": "Nature/Springer Nature",
    "10.1056": "NEJM",
    "10.1136": "BMJ",
    # ... full list in publisher_prefixes.json
}

def check_prefix_journal_alignment(doi, claimed_journal):
    prefix = doi.split("/")[0]
    expected_publisher = PUBLISHER_PREFIXES.get(prefix)
    if expected_publisher and claimed_journal not in expected_publisher:
        flag("PREFIX_JOURNAL_MISMATCH")
```

#### Gap 13: Inverted Statistics (Value-Label Swap)

**Pattern:** The cited paper contains the correct numerical values, but the inline text assigns them to the wrong metric labels. For example, a paper reporting 33% sensitivity and 83% specificity is cited as showing 63% sensitivity and 13% specificity (or vice versa).

**Example (discovered February 12, 2026):** Wong et al., 2021 (Epic Sepsis Model) in a second corpus: the inline text reported sensitivity 63%, specificity 13%, PPV 5%. The actual paper values are sensitivity 33%, specificity 83%, PPV 12%. The meta description in the same file correctly stated 33% sensitivity, creating an intra-document contradiction.

**Why it's missed:** Keyword-matching content verifiers detect that the numbers "33" and "83" appear in the source paper and flag the citation as aligned. String-presence checks cannot determine whether specific numbers are assigned to the correct labels. This error type requires structured extraction of metric-value pairs from both the inline text and the source paper, followed by label-value alignment comparison.

**Detection Enhancement:** Implement structured metric extraction in Phase 2:
```python
def extract_metric_value_pairs(text):
    """Extract {metric_name: value} pairs from text."""
    patterns = [
        r'(sensitivity|specificity|PPV|NPV|AUC|AUROC)[:\s]+(\d+\.?\d*)\s*%',
        r'(\d+\.?\d*)\s*%\s*(sensitivity|specificity|PPV|NPV|AUC|AUROC)',
    ]
    return {metric: value for metric, value in matches}

def compare_metric_pairs(inline_pairs, source_pairs):
    """Flag when values exist in source but are assigned to different labels."""
    for metric, value in inline_pairs.items():
        if metric in source_pairs and source_pairs[metric] != value:
            if value in source_pairs.values():
                flag("INVERTED_STATISTICS")
```

#### Gap 14: Fabricated Code Repositories

**Pattern:** LLMs generate plausible GitHub URLs for tools, frameworks, checklists, or assessment instruments that do not exist. These URLs follow correct GitHub URL patterns (e.g., `github.com/organization/repository-name`) and may reference plausible organizations, but the repositories have never existed.

**Example (discovered February 2026):** Five fabricated GitHub repositories were found in a single chapter on pilot project implementation: `FMEA-AI`, `pilot-assessment`, `ai-pilot-toolkit`, and others. All returned HTTP 404.

**Why it's missed:** Standard academic citation verification focuses on DOI resolution and journal databases. GitHub repositories are not indexed in CrossRef, PubMed, or other academic registries. Phase 1 URL checking will catch the 404 status, but the error is categorized as a generic "broken link" rather than recognized as a fabricated tool/resource.

**Detection Enhancement:** Add repository-specific verification between Phase 1 and Phase 2:
```python
def verify_repository(url):
    """Check if a code repository actually exists."""
    if 'github.com' in url:
        # Use GitHub API for existence check
        api_url = url.replace('github.com', 'api.github.com/repos')
        response = requests.get(api_url)
        if response.status_code == 404:
            return "FABRICATED_REPOSITORY"
    # Extend for GitLab, Bitbucket, etc.
```

#### Gap 15: Generic URL Resolution (Specific-to-General Drift)

**Pattern:** A citation references a specific document (e.g., "MDCG 2019-11 Guidance on Qualification of Software"), but the URL resolves to a top-level page (e.g., `health.ec.europa.eu/`) or a document listing page rather than the specific document. The URL returns HTTP 200, passing Phase 1, but the destination lacks the specific content referenced.

**Example (discovered February 12, 2026):** MDCG 2019-11 guidance document cited with a URL that previously resolved to the PDF but now returns the EU Health website's document download page with a different structure, yielding a 404 for the specific filename.

**Why it's missed:** Phase 1 checks HTTP status codes. A 200 response on a landing page passes. Phase 2 keyword matching may find topically related terms on the landing page (e.g., "medical devices," "software"), producing a false positive alignment score.

**Detection Enhancement:** Compare URL specificity to citation specificity:
```python
def check_url_specificity(citation_text, url, page_content):
    """Flag when citation references specific document but URL is generic."""
    # Extract document identifiers from citation text
    doc_ids = extract_document_identifiers(citation_text)
    # e.g., "MDCG 2019-11", "ISO 14971", "21 CFR 820"

    # Check if specific identifiers appear in page content
    for doc_id in doc_ids:
        if doc_id not in page_content:
            flag("GENERIC_URL", f"Citation references '{doc_id}' but page does not contain it")
```

#### Gap 16: Paper-Implementation Alignment Drift

**Pattern:** The paper documents a methodology (e.g., five phases) but the implementing scripts do not fully implement the documented methodology. Over time, the paper and scripts diverge as either is updated independently.

**Example (discovered February 12, 2026):** The paper documents Phase 0 (DOI existence validation via CrossRef) as the first and distinguishing phase of the pipeline. However, the implementing script (`verification_pipeline.py`) excludes Phase 0 from the CLI argument parser (`choices=[1, 2, 3]` on line 596), making Phase 0 uninvocable. The default phase set is `[1, 2, 3]`, skipping Phase 0 entirely. Additionally, the content verifier (Phase 2) uses a 30% keyword overlap threshold that is far below the specificity described in the paper's methodology, and the metadata verifier (Phase 3) only queries CrossRef for DOI-based URLs, leaving non-DOI citations (PubMed, GitHub, government sites) with zero metadata verification.

**Why it's missed:** Paper review and code review are separate activities. A paper can describe an ideal methodology while the implementing code reflects an earlier or simplified version. This is analogous to documentation drift in software engineering.

**Detection Enhancement:** Implement a paper-code alignment test suite:
```python
def test_phase_coverage():
    """Verify all documented phases are invocable."""
    parser = build_argument_parser()
    for phase in [0, 1, 2, 3]:
        assert phase in parser.get_default('phases') or phase in allowed_choices

def test_content_verifier_depth():
    """Verify content verifier implements documented methodology."""
    # Check keyword threshold is documented value
    # Check content extraction length matches documented approach
    # Check statistics verification goes beyond string presence
```

#### Gap 17: Chimera Citation Pattern

**Discovered:** February 2026, during cross-corpus validation of a second medical AI handbook.

**Pattern:** The LLM constructs a citation by harvesting verified components from a real paper (first author, specific statistics, institutional affiliation) and assembling them into a non-existent publication with a fabricated venue, DOI, and elaborated findings.

**Canonical example:** A citation attributed to "Basu et al., 2026, BMJ Health & Care Informatics" (DOI: 10.1136/bmjhci-2025-101935) combined real statistics (37% race-group disparity reduction, 28% sex-group disparity reduction) from a genuine JMIR AI paper (Basu et al., 2025, DOI: 10.2196/74264) with fabricated elaborations (reasoning motifs, conformal safety envelopes, error taxonomy) that do not exist in the source paper.

**Why existing defenses fail:**
1. **Author verification passes**: Sanjay Basu is a real researcher at Harvard/Waymark
2. **Statistics verification passes**: The 37% and 28% figures appear in the real JMIR AI paper
3. **Institutional verification passes**: The affiliation is real
4. **Topic alignment passes**: Both the real and fabricated papers concern Medicaid AI fairness
5. **DOI format check passes**: The fabricated DOI follows valid BMJ prefix conventions (10.1136)

**Detection requires multi-factor cross-verification:**
- The specific DOI must resolve to a paper with the specific claimed author AND claimed venue
- No single-factor check (author exists? statistics appear in literature? DOI prefix valid?) is sufficient
- The chimera pattern is designed (by the LLM's generation process) to satisfy each verification check in isolation

**Propagation risk:** In the observed case, the chimera appeared in two files (an ethics chapter and an evaluation chapter). The second file contained substantially more fabricated detail (five reasoning motifs, conformal safety envelope specifications, error taxonomy with specific percentages), suggesting the LLM elaborated on its own prior fabrication across sessions.

**Proposed detection method:** Add a mandatory cross-verification step: after confirming author and statistics independently, verify that the specific DOI resolves to a page containing both the claimed author AND the claimed statistics in the same document. If the DOI does not exist or resolves to a different paper, flag as CHIMERA_CITATION regardless of how many individual components verify.

#### Gap 18: Fabrication Propagation with Escalating Detail

**Discovered:** February 2026, during the same cross-corpus validation.

**Pattern:** When a fabricated citation appears in one file and is later referenced in another file (potentially in a different session), the LLM generates increasingly elaborate fabricated detail around the original fabrication. Each successive mention adds specificity that makes the fabrication appear more thoroughly researched.

**Canonical example:**
- **File 1 (ethics chapter):** Cited "Basu et al., 2026" with two statistics (37%, 28%) and a general description of fairness optimization
- **File 2 (evaluation chapter):** Same citation elaborated into a table of five named reasoning motifs with specific detection rates, a detailed conformal safety envelope specification, and an error taxonomy with three categories and precise percentage breakdowns (48%/27%/25%)

**Why this is distinct from simple duplication:** The content in File 2 is not copied from File 1. It is new fabricated material that the LLM generated to provide "depth" around the already-fabricated citation. This creates a false sense of cross-validation: if an auditor checks File 1 and sees a citation, then finds the same citation with even more detail in File 2, it appears more credible.

**Detection method:** After identifying any fabricated citation, grep for all instances across the entire corpus. Compare detail levels. If later instances contain substantially more specific claims than earlier ones (especially structured data like tables, taxonomies, or named frameworks), treat the additional detail as fabricated unless independently verified.

**Implication for verification workflow:** Citation audits must be cross-file, not per-file. A per-file audit may verify the simple mention in File 1 and miss the elaborate fabrication in File 2, or vice versa.

#### Gap 19: Government Database Bot-Blocking False Positives

**Discovered:** February 2026, during URL verification of regulatory citations.

**Pattern:** Government databases and regulatory portals (e.g., FDA accessdata.fda.gov, NIH databases, EU regulatory portals) return HTTP 403 Forbidden or 404 Not Found to automated verification requests while remaining fully accessible to human users in a browser. The citation is valid and the URL is correct, but automated Phase 1 verification flags it as broken.

**Canonical example:** FDA device clearance pages at `accessdata.fda.gov/scripts/cdrh/cfdocs/cfpmn/pmn.cfm?ID=KXXXXXX` returned 403 to automated HTTP requests (including WebFetch) despite being fully accessible in a browser. This created false positives that consumed verification resources and risked incorrect correction of valid citations.

**Why existing defenses fail:**
1. Phase 1 URL resolution classifies any non-200 response as an error
2. No distinction between bot-blocking (valid page, restricted access) and genuine 404 (page does not exist)
3. CrossRef API (Phase 0) does not index government regulatory databases
4. Government sites frequently implement aggressive bot protection without returning standard 403 responses

**Detection enhancement:** Add a government domain allowlist that triggers alternative verification when standard HTTP checks fail:
```python
GOVERNMENT_DOMAINS = {
    'accessdata.fda.gov': 'FDA device database',
    'clinicaltrials.gov': 'Clinical trials registry',
    'ncbi.nlm.nih.gov': 'PubMed/NCBI',
    'health.ec.europa.eu': 'EU Health portal',
}

def verify_government_url(url, domain):
    """When standard fetch returns 403/404, try alternative verification."""
    # 1. Check if domain is in government allowlist
    # 2. Extract document identifier from URL (e.g., 510(k) number)
    # 3. WebSearch for the document identifier to confirm existence
    # 4. If WebSearch confirms, classify as VERIFIED_BOT_BLOCKED (not BROKEN_URL)
```

**Implication for error rate reporting:** False positives from bot-blocked government sites inflate the apparent broken URL rate. Verification reports should distinguish BROKEN_URL from BOT_BLOCKED_URL to avoid misrepresenting the actual error rate.

#### Gap 20: Same-Topic Qualitative Finding Misrepresentation

**Discovered:** February 2026, during cross-file content verification.

**Pattern:** The correct paper is cited for the correct general topic, but the specific qualitative finding described in the inline text is wrong. Unlike INVERTED_STATISTICS (Gap 13), which involves numerical values assigned to wrong labels, this pattern involves misrepresenting the paper's conclusions, direction of effect, or key finding.

**Canonical example:** A paper studying AI-assisted triage is cited as finding "AI improved triage accuracy" when the actual conclusion was "AI did not significantly improve triage accuracy compared to experienced clinicians." The paper, topic, and author are all correct; only the described finding is wrong.

**Why existing defenses fail:**
1. Phase 1 passes (URL resolves correctly)
2. Phase 2 keyword matching passes (paper is about AI triage, citation claims are about AI triage)
3. Phase 3 passes (author, year, and journal are all correct)
4. Even structured metric extraction (Gap 13 enhancement) may miss this because the error is qualitative, not quantitative

**Detection enhancement:** Extend Phase 2 content verification to include directional claim extraction:
```python
def extract_claim_direction(text):
    """Extract the direction of effect claimed in inline text."""
    positive_signals = ['improved', 'reduced', 'increased accuracy', 'outperformed']
    negative_signals = ['did not improve', 'no significant difference', 'failed to']
    neutral_signals = ['comparable', 'similar', 'equivalent']
    # Compare direction in inline claim vs. paper conclusion
```

**Distinction from related gaps:**
- Gap 3 (CLAIM_MISMATCH): Paper and claim are on different topics
- Gap 13 (INVERTED_STATISTICS): Numerical values swapped between labels
- Gap 20 (this gap): Same topic, but qualitative finding (direction of effect) misrepresented

#### Gap 21: Trial and Study Identity Confusion

**Discovered:** February 2026, during specialty chapter verification.

**Pattern:** Distinct clinical trials or studies that share investigators, institutions, or topic areas are conflated into a single citation. The LLM attributes findings from Trial A to Trial B because the same researcher led both, or because both trials studied the same intervention at the same institution.

**Canonical example:** A researcher who led both a 2019 feasibility study (n=50) and a 2022 randomized controlled trial (n=500) on the same AI diagnostic tool is cited once with the 2022 DOI but with the sample size and preliminary findings from the 2019 study. Both papers exist and both are by the same first author; the error is conflation of distinct studies.

**Why existing defenses fail:**
1. Phase 0 passes (DOI exists in CrossRef)
2. Phase 1 passes (URL resolves)
3. Phase 3 partially passes (author name matches, year matches the DOI paper)
4. Phase 2 keyword matching passes (both studies cover the same topic)
5. Even structured metric extraction may match on some overlapping metrics

**Detection enhancement:** When Phase 2 identifies a statistical claim that does not match the resolved paper but is topically aligned, search for other publications by the same first author:
```python
def check_author_study_conflation(author, year, claimed_stats, resolved_paper_stats):
    """Check if claimed statistics come from a different study by same author."""
    if claimed_stats != resolved_paper_stats:
        # Search for other papers by this author on same topic
        other_papers = crossref_search(author, topic_keywords)
        for paper in other_papers:
            if paper.stats match claimed_stats:
                flag("TRIAL_IDENTITY_CONFUSION",
                     f"Statistics appear to come from {paper.doi}, not {resolved_doi}")
```

**Implication:** This error type is structurally similar to CHIMERA_CITATION (Gap 17) but involves two real papers rather than a real paper and a fabricated venue. The LLM is not fabricating; it is conflating, which makes it harder to detect because all components are individually verifiable.

### 2.8 Verification Protocol

Each citation underwent the following standardized protocol:

```
FOR each citation IN corpus:

    # Phase 1
    response = web_fetch(citation.url)
    IF response.status == 404:
        flag_as_broken()
        CONTINUE

    # Phase 2
    paper_content = extract_content(response)
    inline_claim = extract_surrounding_text(citation, 200_chars)
    alignment = compare_claim_to_content(inline_claim, paper_content)
    IF alignment == "mismatch":
        flag_claim_mismatch()

    # Phase 3
    extracted_metadata = parse_metadata(response)
    citation_metadata = parse_citation_text(citation)
    discrepancies = compare_metadata(extracted_metadata, citation_metadata)
    IF discrepancies:
        flag_metadata_errors(discrepancies)

    # Phase 4
    IF any_errors_flagged():
        correction = determine_correction(error_type)
        apply_correction(citation, correction)
        verify_correction()
```

### 2.9 Quality Assurance

To ensure verification accuracy, we implemented:

1. **Double Verification:** All flagged errors verified through independent search
2. **Cross-File Consistency:** Citations appearing in multiple chapters verified for consistent correction
3. **Post-Correction Validation:** Each corrected citation re-verified through Phase 1-3
4. **Negative Control:** 20 random "verified correct" citations re-checked to confirm true negative rate

### 2.10 Comparison Methods

To contextualize our findings, we compared our methodology against:

1. **Automated Link Checking:** Standard HTTP status code verification only
2. **DOI Validation:** Syntax validation + resolution testing
3. **Reference Manager Verification:** Format consistency checking
4. **Random Sampling Manual Review:** Traditional peer review simulation

### 2.11 Statistical Analysis

Descriptive statistics were calculated for:
- Overall error rate (errors/total citations)
- Error rate by category
- Error rate by chapter/section
- Detection rate by method

Chi-square tests assessed differences in error rates between chapters and between error types. Significance threshold: p < 0.05.

---

## 3. Results

### 3.1 Overall Error Rates

Of 150 unique citations verified, 70 (46.7%) contained at least one error.

**Table 1: Overall Verification Results**

| Metric | Count | Percentage |
|--------|-------|------------|
| Total citations verified | 150 | 100% |
| Citations with errors | 70 | 46.7% |
| Citations verified correct | 80 | 53.3% |
| Citations with multiple errors | 8 | 5.3% |
| Total individual errors | 78 | — |

### 3.2 Error Distribution by Category

**Table 2: Error Distribution by Type**

| Error Category | Count | % of Errors | % of Total Citations |
|---------------|-------|-------------|---------------------|
| Wrong Paper | 18 | 25.7% | 12.0% |
| Broken DOI/URL | 15 | 21.4% | 10.0% |
| Year Error | 9 | 12.9% | 6.0% |
| Author Error | 8 | 11.4% | 5.3% |
| Claim Mismatch | 7 | 10.0% | 4.7% |
| Journal Error | 7 | 10.0% | 4.7% |
| Metric Error | 6 | 8.6% | 4.0% |
| Fabricated | 1 | 1.4% | 0.7% |
| **Total** | **70** | **100%** | **46.7%** |

### 3.3 Error Distribution by Content Type

**Table 3: Error Rates by Content Complexity**

| Content Type | Citations | Errors | Error Rate |
|--------------|-----------|--------|------------|
| **Foundational/Historical** | 47 | 10 | 21.3% |
| **Specialized/Applied** | 103 | 60 | 58.3% |

**Observation:** Error rates vary significantly by content type. Specialized content requiring domain-specific citations exhibited nearly 3x higher error rates than foundational content with more commonly cited references.

The difference in error rates between foundational (21.3%) and specialized content (58.3%) was statistically significant (χ² = 18.4, p < 0.001).

**Implication for Comparative LLM Testing:** When comparing citation accuracy across LLM systems, test corpora should include both foundational and specialized content to capture the full error rate spectrum.

### 3.4 Detection Capability by Method

**Table 4: Error Detection by Verification Method**

| Method | Errors Detected | Detection Rate | Errors Missed |
|--------|-----------------|----------------|---------------|
| Phase 1 only (URL check) | 15 | 21.4% | 55 |
| Phase 1-2 (+ Content) | 46 | 65.7% | 24 |
| Phase 1-3 (+ Metadata) | 70 | 100% | 0 |
| Automated link checker | 15 | 21.4% | 55 |
| DOI syntax validation | 3 | 4.3% | 67 |
| Reference manager | 0 | 0% | 70 |

**Key Finding:** Automated link checking detected only 21.4% of errors. The remaining 78.6% required content-level or metadata verification.

### 3.5 Error Type by Detection Phase

**Table 5: Which Phase Detects Which Errors**

| Error Type | Phase 1 | Phase 2 | Phase 3 |
|------------|---------|---------|---------|
| Broken DOI/URL | ✓ | — | — |
| Wrong Paper | — | ✓ | — |
| Claim Mismatch | — | ✓ | — |
| Metric Error | — | ✓ | — |
| Author Error | — | — | ✓ |
| Year Error | — | — | ✓ |
| Journal Error | — | — | ✓ |
| Fabricated | ✓* | ✓ | ✓ |

*Fabricated citations may present as broken URLs or may resolve to unrelated content

### 3.6 Specific Error Examples

#### 3.6.1 Wrong Paper (Most Common Error)

**Example: Zhao et al. Fetal Heart Rate Study**

*Original Citation:*
```
([Zhao et al., 2019](https://doi.org/10.1016/j.eswa.2019.02.008))
```

*Inline Claim:* "Deep learning approach for fetal heart rate classification achieved 98% accuracy"

*Actual Paper at DOI:* "A multi-agent dynamic system for robust multi-face tracking"

*Analysis:* The DOI resolved successfully (would pass automated check) but pointed to a computer vision paper about face tracking, entirely unrelated to fetal heart rate analysis.

*Correction:* Found correct paper via search:
```
([Zhao et al., 2019](https://doi.org/10.1186/s12911-019-0891-1))
```

#### 3.6.2 Author Attribution Error

**Example: Botta vs. Arnal**

*Original Citation:*
```
([Arnal et al., 2021](https://pubmed.ncbi.nlm.nih.gov/34047244/))
```

*Verification:* PubMed page clearly shows first author as "Botta M" not "Arnal"

*Correction:*
```
([Botta et al., 2021](https://doi.org/10.1186/s13054-021-03611-y))
```

#### 3.6.3 Metric Error

**Example: Wong et al. Specificity Value**

*Original Text:* "showed 33% sensitivity and 67% specificity"

*Actual Paper Values:* Sensitivity 33% (correct), Specificity 83% (not 67%)

*Correction:* Changed "67% specificity" to "83% specificity"

#### 3.6.4 Fabricated Citation

**Example: Green et al. Cardiac Arrest Study**

*Original Citation:*
```
([Green et al., 2019](https://doi.org/10.1001/jamanetworkopen.2019.14004))
```

*Claim:* "35% reduction in cardiac arrests outside ICU"

*Verification:*
- DOI returned 404
- Exhaustive search found no paper by "Green et al." on this topic
- No Michigan Medicine publication matching description
- Conclusion: Citation is fabricated

*Resolution:* Removed specific claim, replaced with general statement without citation

### 3.7 Correction Success Rate

**Table 6: Correction Outcomes**

| Outcome | Count | Percentage |
|---------|-------|------------|
| Replaced with correct citation | 52 | 74.3% |
| Corrected metadata only | 15 | 21.4% |
| Claim rephrased to match citation | 2 | 2.9% |
| Claim removed (unverifiable) | 1 | 1.4% |
| **Total corrections** | **70** | **100%** |

### 3.8 Time and Resource Requirements

**Table 7: Verification Effort by Phase**

| Phase | Time per Citation | Skill Required |
|-------|-------------------|----------------|
| Phase 1 (URL) | 30 seconds | Automated |
| Phase 2 (Content) | 3-5 minutes | Domain expertise |
| Phase 3 (Metadata) | 1-2 minutes | Basic research skills |
| Phase 4 (Correction) | 5-10 minutes | Domain expertise + search skills |

**Total Project Time:** Approximately 25 hours for 150 citations

**Parallelization:** Phases 1-3 can be parallelized across chapters, reducing wall-clock time to approximately 8 hours with multiple concurrent reviewers.

### 3.9 Cross-Corpus Validation and Paper-Implementation Gap Analysis (February 2026)

To assess the generalizability of the methodology and the fidelity of the automated implementation, we applied both the automated verification pipeline and manual expert-driven verification to a second corpus: a 39-chapter medical AI handbook produced using the same LLM-assisted authoring workflow.

#### 3.9.1 Automated Pipeline Results

Running the automated pipeline on a representative chapter (an implementation/safety chapter, 23 total citations, 19 unique) produced:

**Table 8: Automated Pipeline Results on Second Corpus (Single Chapter)**

| Metric | Count |
|--------|-------|
| Total citations | 23 |
| Unique citations | 19 |
| Verified correct | 9 |
| Broken URLs | 2 |
| Unable to verify | 8 |
| Error rate (detected) | 10.5% |

The automated pipeline detected only 2 errors (both broken URLs), with 8 citations (42%) classified as "unable to verify" due to paywalled content or JavaScript-rendered pages.

#### 3.9.2 Manual Expert-Driven Verification Results

Parallel manual verification of the same chapter by expert agents using enhanced methods (WebSearch fallback, full-text reading, cross-file consistency checking) identified 10 errors:

**Table 9: Manual Verification Results on Same Chapter**

| Error Type | Count | Automated Detection |
|------------|-------|---------------------|
| Broken URL | 2 | Detected |
| Inverted statistics | 1 | **Missed** |
| Fabricated citation (DOI does not exist) | 1 | **Missed** |
| Fabricated repository | 1 | **Missed** (classified as broken URL) |
| Wrong paper (topically related, claim unsupported) | 2 | **Missed** (unable to verify) |
| Generic URL (landing page, not specific document) | 1 | **Missed** |
| Metric error (wrong values) | 2 | **Missed** |

**Key finding:** The automated pipeline detected 2 of 10 errors (20% detection rate), consistent with the paper's documented finding that automated link checking catches only ~21% of errors. However, this comparison reveals that the automated scripts do not implement the full methodology documented in this paper. Specifically:

1. Phase 0 (DOI existence validation) was not invoked because the CLI argument parser excludes it
2. Phase 2 (content-claim alignment) detected no wrong-paper errors because the keyword overlap threshold (30%) was too permissive
3. Phase 3 (metadata verification) did not verify non-DOI citations because it only queries CrossRef

#### 3.9.3 Detection Method Comparison

**Table 10: Detection Methods Used by Manual Agents vs Automated Scripts**

| Method | Automated Script | Manual Agents |
|--------|-----------------|---------------|
| HTTP status code check | Yes | Yes |
| CrossRef DOI lookup | Excluded (bug) | Via WebSearch |
| Keyword overlap for topic alignment | Yes (30% threshold) | No (full-text reading) |
| String presence for statistics | Yes (presence only) | No (value-label pair matching) |
| WebSearch fallback for paywalled content | No | Yes |
| GitHub API / repository existence check | No | Yes (WebFetch) |
| Cross-file consistency checking | No | Yes |
| Intra-document consistency checking | No | Yes |
| DOI prefix-to-journal validation | In code but not active | Yes |
| Metric-label alignment verification | No | Yes |

#### 3.9.4 The Inverted Statistics Case

The most significant finding from the cross-corpus validation was the INVERTED_STATISTICS error type. In the Wong et al. (2021) Epic Sepsis Model citation:

- **Inline text stated:** Sensitivity 63%, Specificity 13%, PPV 5%, 22,000+ false alarms
- **Actual paper values:** Sensitivity 33%, Specificity 83%, PPV 12%, 6,971 alerts over ~10 months
- **Meta description in same file:** Correctly stated 33% sensitivity

This error is undetectable by any existing automated approach because:
1. The URL resolves correctly (Phase 1 passes)
2. The paper is topically aligned and keywords match (Phase 2 passes with keyword matching)
3. The numbers "33" and "83" appear in the source (string presence checks pass)
4. The author, year, and journal are correct (Phase 3 passes)

Only structured extraction of metric-value pairs from both inline text and source paper, followed by label-value alignment comparison, can detect this error type. This represents a new category requiring Phase 2 enhancement beyond keyword matching.

#### 3.9.5 Implications for Methodology-Implementation Alignment

The cross-corpus validation revealed a meta-finding: **the gap between documented methodology and implemented tooling is itself a verification target**. The paper documents a five-phase pipeline, but the scripts implement approximately 2.5 of those phases (Phase 1 fully, Phase 2 partially, Phase 3 partially). This "paper-implementation drift" is analogous to documentation drift in software engineering and represents Gap 16 in the extended gap analysis (Section 2.7).

We recommend periodic paper-code alignment testing: a test suite that verifies all documented phases are invocable, all documented error types are detectable, and all documented thresholds match implementation values.

#### 3.9.6 Chimera Citation Discovery

Continued cross-corpus validation of the second medical AI handbook (February 2026) identified a new error category, CHIMERA_CITATION, not previously documented in any verification literature. A citation attributed to "Basu et al., 2026, BMJ Health & Care Informatics" combined real statistics from a genuine JMIR AI paper (Basu et al., 2025, DOI: 10.2196/74264) with a fabricated journal venue, fabricated DOI (10.1136/bmjhci-2025-101935), and fabricated elaborations (reasoning motifs, conformal safety envelopes).

The chimera appeared in two files with escalating detail: the ethics chapter contained a single paragraph with two statistics, while the evaluation chapter contained the same citation expanded into structured tables, named frameworks, and precise percentage breakdowns, none of which exist in the source paper. This represents the first documented case of fabrication propagation with escalating detail across files (see Gap 17, Gap 18 in Section 2.7).

**Detection failure analysis:** All five layers of the defense architecture failed to catch this chimera:
- Layer 1 (behavioral rules): The citation followed correct formatting conventions
- Layer 2 (PostToolUse hook): No network calls; DOI format was syntactically valid
- Layer 3 (pre-commit): No content-level verification
- Layer 4 (on-demand pipeline): Not run against this file during initial authoring
- Layer 5 (registry): Citation was not in verified-citations.json, but unverified citations generate non-blocking warnings only

**Implication:** Chimera citations require a dedicated detection step that cross-references the claimed DOI, author, and venue as a triple, not as independent checks. This has been added to the error taxonomy (Section 2.5) and gap analysis (Section 2.7, Gaps 17-18).

---

## 4. Discussion

### 4.1 Principal Findings

Our systematic verification of 150 citations in LLM-assisted medical text revealed a 46.7% error rate, substantially higher than would be acceptable in peer-reviewed literature. More critically, only 21.4% of these errors would be detected by automated link-checking tools, meaning 78.6% require content-level human verification.

The most common error type—"wrong paper" (25.7%)—represents a particularly insidious failure mode. These citations pass all automated checks: the DOI is syntactically valid, the URL resolves successfully, and a real paper exists at the destination. Only content-level analysis reveals that the paper has nothing to do with the claim it ostensibly supports.

### 4.2 Comparison with Prior Literature

Our 46.7% error rate aligns with previous studies of LLM citation accuracy:

- Alkaissi & McFarlane (2023) found ChatGPT fabricated 47% of citations in generated medical abstracts
- Walters & Wilder (2023) reported 72% of GPT-4 generated references contained errors
- Huang & Tan (2023) found 53% hallucination rate in legal citations

However, our study extends prior work by:
1. Developing a comprehensive error taxonomy beyond binary "correct/fabricated"
2. Quantifying the detection capability gap between automated and content-level verification
3. Demonstrating the methodology in a realistic LLM-assisted authorship scenario (human-edited, not purely generated)

### 4.3 Comparison with Existing Verification Tools

Our methodology addresses limitations in existing citation verification tools that operate at different levels of the verification stack:

**Table 11: Comparison with Existing Citation Verification Approaches**

| Tool/Approach | Verification Level | Error Types Detected | Error Types Missed |
|---------------|-------------------|---------------------|-------------------|
| **Scite.ai** | Smart citations (supporting/contrasting classification) | Identifies whether citing papers support or contradict claims | Does not verify DOI correctness, metadata accuracy, or detect fabricated citations |
| **Semantic Scholar** | Citation graph analysis, paper metadata | Validates paper existence, retrieves metadata | Does not verify claim-citation alignment or detect metric errors |
| **Retraction Watch** | Retracted paper identification | Flags citations to retracted papers | Limited to retraction database; does not detect other error types |
| **CrossRef API** | DOI resolution and metadata | Validates DOI existence (Phase 0), provides authoritative metadata | No content-level verification; cannot assess claim support |
| **Standard link checkers** | HTTP status code verification | Broken URLs (Phase 1 only, 21.4% of errors) | All content-level errors (78.6% of errors) |
| **Reference managers** (Zotero, EndNote) | Format consistency | Formatting errors | Zero content or accuracy errors detected |
| **SourceCheckup** (Wu et al., 2024) | LLM response-level support assessment | Classifies LLM responses as supported/unsupported by cited sources | Designed for LLM responses to queries, not for document-level citation audits |
| **Our five-phase pipeline** | DOI existence + URL + content + metadata | All 16 error categories | Requires human judgment for Phase 2; bot-blocked URLs create false positives |

**Key differentiators of our approach:**

1. **Phase 0 (DOI existence):** No existing tool systematically checks whether DOIs exist in the CrossRef registry before attempting resolution. This distinguishes fabricated DOIs from broken links, a critical distinction for understanding LLM failure modes.

2. **Content-claim alignment (Phase 2):** Scite.ai classifies citation sentiment (supporting/contrasting) but does not verify whether specific claims in the citing text match findings in the cited paper. Our Phase 2 addresses the specific gap where a real paper is cited for a finding it does not contain.

3. **Multi-factor cross-verification:** Chimera citations (Gap 17) pass every single-factor verification tool. Only our cross-verification approach (verifying DOI + author + venue as a connected triple) detects this pattern.

4. **Defense-in-depth architecture:** Existing tools operate as point solutions. Our five-layer architecture integrates verification throughout the content lifecycle, from generation-time behavioral rules to a verified citations registry.

### 4.4 Implications for Medical and Scientific Publishing

The high error rate observed has significant implications:

**For Authors Using LLM Assistance:**
- All LLM-generated citations must be individually verified
- URL validity alone is insufficient; content alignment must be confirmed
- Citation verification should be treated as a mandatory step, not optional polish

**For Journals and Publishers:**
- Current peer review processes are insufficient to detect LLM citation errors
- Automated screening tools detect only ~20% of errors
- Enhanced verification protocols are needed for manuscripts acknowledging LLM assistance

**For Readers and Researchers:**
- Citations in LLM-assisted content cannot be trusted without verification
- Papers citing LLM-assisted sources should verify those citations
- Citation chains may propagate errors from LLM-generated content

### 4.5 Why Content-Level Verification Is Essential

Our finding that 78.6% of errors require content-level verification deserves emphasis. The LLM failure mode is not simply generating fake DOIs—it is generating plausible citations to real papers that do not support the claims made.

This represents a qualitatively different challenge from traditional citation errors (typos, formatting issues). It requires understanding both:
1. What the inline text claims
2. What the cited paper actually demonstrates

Only a human reviewer with domain expertise can reliably assess this alignment.

### 4.6 The Error Rate Gradient

The statistically significant difference in error rates between Part 1 (21.3%) and Part 2 (58.3%) suggests that error rates vary with:

- **Content Specificity:** Highly specialized content (subspecialty applications) had higher error rates
- **Citation Density:** Chapters with more citations per unit text had higher error rates
- **Source Availability:** Topics with fewer canonical references had higher error rates

This gradient has practical implications: verification resources should be concentrated on more specialized, citation-dense sections.

### 4.7 Paper-Implementation Alignment as a Meta-Verification Target

A novel finding from the cross-corpus validation (Section 3.9) is that **the gap between documented methodology and implemented tooling is itself a significant source of verification failure**. Our automated scripts implemented approximately 2.5 of the 5 documented phases:

| Phase | Paper Description | Script Implementation | Gap |
|-------|-------------------|----------------------|-----|
| Phase 0 | DOI existence via CrossRef | CLI parser excludes Phase 0 (`choices=[1,2,3]`) | Phase uninvocable |
| Phase 1 | URL resolution | Fully implemented | None |
| Phase 2 | Content-claim alignment | 30% keyword overlap threshold; first 5000 chars only | Shallow implementation |
| Phase 3 | Metadata verification | CrossRef-only (DOI URLs); no PubMed, no publisher pages | DOI-only coverage |
| Phase 4 | Correction | Not implemented in scripts (manual process) | By design |

This paper-implementation drift has a direct analogue in software engineering: documentation that describes desired behavior while code implements a subset. The practical consequence is that users running the pipeline with default settings invoke a methodology substantially weaker than what the paper documents.

**Recommendation:** Verification methodologies intended for reproducibility should include a paper-code alignment test suite that programmatically verifies all documented phases are invocable, all error categories are detectable, and all documented parameters match implementation values. This test suite should run as part of the repository's continuous integration pipeline.

### 4.8 Methodology Limitations

Several limitations should be acknowledged:

1. **Corpus scope:** Initial findings derive from one corpus of LLM-assisted medical content, with cross-corpus validation on a second (Section 3.9). The 46.7% error rate reflects a specific authoring workflow (LLM-assisted drafting with human editing); purely LLM-generated content or purely human-authored content may exhibit different rates. Broader replication across domains, authoring workflows, and document types is needed.
2. **Domain specificity:** Medical AI citations may differ from other domains. Citation patterns in legal, policy, or engineering literature remain uncharacterized by this methodology.
3. **LLM version dependency:** Citation patterns may vary across model versions, prompting strategies, and retrieval-augmented generation configurations. Our findings reflect a specific LLM and workflow; longitudinal tracking across model versions would strengthen generalizability claims.
4. **Single-reviewer verification:** Content-claim alignment assessment (Phase 2) was performed by a single expert reviewer. Inter-rater reliability was not assessed. Phase 2 decisions involve subjective judgment about whether a paper "supports" a specific claim, particularly for partial matches.
5. **Access limitations:** Approximately 42% of citations in the cross-corpus validation were classified as "unable to verify" due to paywalled content, JavaScript-rendered pages, or bot-blocking (Gap 19). This represents a substantial portion of citations where automated and semi-automated methods may miss errors.
6. **Paper-implementation drift:** The gap between documented methodology and automated implementation (Section 4.6) means that published detection rates reflect the full methodology, not the automated subset. Users of the automated tools alone should expect lower detection rates than reported here.
7. **Temporal validity:** Citations verified as correct at verification time may become incorrect through retraction, correction, or URL changes. The methodology captures a snapshot; periodic re-verification is needed.
8. **False positive rate:** Bot-blocked URLs (Gap 19) inflate the apparent broken URL rate. The distinction between genuinely broken URLs and bot-blocked valid URLs requires manual follow-up that is not fully automated.

### 4.9 Recommendations

Based on our findings, we recommend:

**For Immediate Implementation:**
1. All LLM-assisted medical/scientific content should undergo systematic citation verification
2. Verification should include content-claim alignment, not just URL testing
3. Organizations should develop verification checklists based on our five-phase pipeline
4. Automated scripts should include WebSearch fallback for paywalled content to reduce "unable to verify" rates
5. Metric-value pair extraction should replace simple string-presence checks for statistical claims

**For Journal Policies:**
1. Manuscripts acknowledging LLM assistance should require citation verification attestation
2. Random citation audits should be implemented for LLM-assisted submissions
3. Automated link checking should be supplemented with content-level spot checks

**For Tooling and Infrastructure:**
1. Verification scripts must implement all documented phases; paper-code alignment tests should be automated
2. Phase 2 content verifiers should implement structured metric-value pair extraction, not keyword overlap
3. "Unable to verify" citations must have an escalation pathway (WebSearch fallback, manual sampling)
4. Non-DOI citations (PubMed, GitHub, government sites) require dedicated verification pathways
5. Code repository URLs require separate existence verification (GitHub API, etc.)
6. Cross-file consistency checking should be a standard post-verification step

**For Future Research:**
1. Development of semi-automated content-claim alignment tools with structured metric extraction
2. Training reviewers in LLM citation error patterns, including inverted statistics
3. Longitudinal tracking of error rates across model versions
4. Evaluation of LLM-as-verifier approaches for Phase 2 content alignment
5. Comparative analysis of verification pipeline performance across different LLM-assisted authoring workflows

### 4.10 Toward Automated Content-Level Verification

While our methodology relies heavily on human judgment, partial automation is possible:

**Automatable Components (Phases 0-1, 3):**
- DOI existence validation via CrossRef API (Phase 0)
- URL resolution testing (Phase 1)
- Metadata extraction from landing pages (Phase 3)
- Cross-reference checking against PubMed/academic databases
- Flagging statistical claims for manual review

**Requiring Human Judgment (Phase 2):**
- Assessing whether paper content supports specific claims
- Determining appropriate corrections for mismatches
- Evaluating partial matches and semantic drift

Future work should develop hybrid human-AI verification systems that automate routine checks while flagging potential content-level mismatches for expert review.

### 4.11 Defense-in-Depth: Beyond Post-Hoc Verification

A critical insight from our implementation work is that post-hoc verification alone is insufficient. By the time verification runs, errors may have proliferated across files, been cited by downstream content, or become embedded in production systems.

The Five-Layer Defense Architecture (Section 2.6) addresses this by integrating verification throughout the content lifecycle:

1. **Prevention** is more efficient than detection (Layer 1)
2. **Real-time feedback** catches errors before they compound (Layer 2)
3. **Commit-time validation** prevents bad citations from entering version control (Layer 3)
4. **Deep verification** catches what automated checks miss (Layer 4)
5. **Registry acceleration** reduces verification overhead for known-good citations (Layer 5)

This defense-in-depth approach is generalizable beyond citation verification to other content integrity challenges in LLM-assisted authoring.

### 4.12 Comparative LLM Testing Framework

This methodology enables systematic comparison of citation accuracy across different LLM systems. We propose the following framework for comparative testing:

#### Target Systems for Comparison

| System | Type | Expected Use Case |
|--------|------|-------------------|
| OpenEvidence | Medical-specialized | Clinical decision support |
| Doximity GPT | Medical-specialized | Physician-facing queries |
| ChatGPT/GPT-4 | General-purpose | Medical content drafting |
| Claude | General-purpose | Research assistance |
| Grok | General-purpose | Real-time information |
| Gemini | General-purpose | Multimodal queries |
| Perplexity | Search-augmented | Citation-focused responses |

#### Standardized Test Protocol

1. **Query Design:** Create 10-20 standardized medical queries requiring cited responses
   - Mix of foundational questions (well-documented topics)
   - Specialized questions (requiring domain-specific citations)
   - Statistical questions (requiring specific numbers)

2. **Response Collection:** Each system responds to identical queries
   - Record full response including all citations
   - Timestamp responses for reproducibility
   - Note any system-specific formatting

3. **Verification Pipeline:** Apply four-phase methodology to all citations
   - Same verification protocol across all systems
   - Blind verification (verifier doesn't know which LLM generated citation)

4. **Metrics for Comparison:**
   - Total error rate by system
   - Error type distribution by system
   - Content-type specific error rates
   - Fabrication rate (completely non-existent citations)
   - Specificity accuracy (error rate for specific statistics)

#### Hypothesis

Based on preliminary observations, we hypothesize:
- Medical-specialized systems may have lower error rates for clinical content
- Search-augmented systems (Perplexity) may have lower fabrication rates
- General-purpose systems may show higher error rates for specialized content
- All systems will show higher error rates for specific statistics than general claims

This framework enables empirical comparison rather than relying on marketing claims about citation accuracy.

---

## 5. Figures

### Figure 1: Five-Phase Verification Pipeline

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    CITATION VERIFICATION PIPELINE                        │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌──────────────────┐                                                   │
│  │   INPUT          │                                                   │
│  │   Citation +     │                                                   │
│  │   Inline Claim   │                                                   │
│  └────────┬─────────┘                                                   │
│           │                                                              │
│           ▼                                                              │
│  ┌──────────────────┐     ┌──────────────────┐                         │
│  │    PHASE 0       │     │   ERROR OUTPUT   │                         │
│  │   DOI Existence  │────▶│   FABRICATED_DOI │                         │
│  │   (CrossRef API) │     │                  │                         │
│  └────────┬─────────┘     └──────────────────┘                         │
│           │ Exists                                                       │
│           ▼                                                              │
│  ┌──────────────────┐     ┌──────────────────┐                         │
│  │    PHASE 1       │     │   ERROR OUTPUT   │                         │
│  │   URL/DOI        │────▶│   BROKEN_URL     │                         │
│  │   Resolution     │     │   (21.4%)        │                         │
│  └────────┬─────────┘     └──────────────────┘                         │
│           │ Pass                                                         │
│           ▼                                                              │
│  ┌──────────────────┐     ┌──────────────────┐                         │
│  │    PHASE 2       │     │   ERROR OUTPUT   │                         │
│  │   Content-Claim  │────▶│   WRONG_PAPER    │                         │
│  │   Alignment      │     │   CLAIM_MISMATCH │                         │
│  │                  │     │   METRIC_ERROR   │                         │
│  └────────┬─────────┘     │   (44.3%)        │                         │
│           │ Pass          └──────────────────┘                         │
│           ▼                                                              │
│  ┌──────────────────┐     ┌──────────────────┐                         │
│  │    PHASE 3       │     │   ERROR OUTPUT   │                         │
│  │   Metadata       │────▶│   AUTHOR_ERROR   │                         │
│  │   Verification   │     │   YEAR_ERROR     │                         │
│  │                  │     │   JOURNAL_ERROR  │                         │
│  └────────┬─────────┘     │   (34.3%)        │                         │
│           │ Pass          └──────────────────┘                         │
│           ▼                                                              │
│  ┌──────────────────┐                                                   │
│  │    PHASE 4       │                                                   │
│  │   Correction &   │                                                   │
│  │   Replacement    │                                                   │
│  └──────────────────┘                                                   │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### Figure 2: Error Distribution by Category

```
Error Type Distribution (n=70)

Wrong Paper      ████████████████████████████  25.7%
Broken DOI       █████████████████████         21.4%
Year Error       █████████████                 12.9%
Author Error     ███████████                   11.4%
Claim Mismatch   ██████████                    10.0%
Journal Error    ██████████                    10.0%
Metric Error     ████████                       8.6%
Fabricated       █                              1.4%

                 0%   5%   10%  15%  20%  25%  30%
```

### Figure 3: Detection Capability Comparison

```
Errors Detected by Verification Method

                            Detected    Missed
                            ────────    ──────
Automated Link Check        ███         ████████████████  (21.4% detected)
                            15          55

DOI Syntax Validation       █           ██████████████████ (4.3% detected)
                            3           67

Reference Manager           ·           ███████████████████ (0% detected)
                            0           70

Phase 1-2 (+ Content)       █████████   ███████            (65.7% detected)
                            46          24

Full Pipeline (1-3)         ████████████                   (100% detected)
                            70          0
```

### Figure 4: Error Rate by Chapter Type

```
Error Rate Comparison

Part 1: Foundations    ██████████████████████         21.3%
                       (10/47 citations)

Part 2: Specialties    ████████████████████████████████████████████████████████  58.3%
                       (60/103 citations)

                       0%        20%        40%        60%        80%

χ² = 18.4, p < 0.001
```

### Figure 5: Error Type Detection by Pipeline Phase

```
                        Phase 0    Phase 1    Phase 2    Phase 3
                        (DOI Reg)  (URL)      (Content)  (Metadata)
                        ─────────  ───────    ─────────  ──────────
FABRICATED_DOI          ●          ○          ○          ○
BROKEN_URL              ○          ●          ○          ○
WRONG_PAPER             ○          ○          ●          ○
CLAIM_MISMATCH          ○          ○          ●          ○
METRIC_ERROR            ○          ○          ●          ○
AUTHOR_ERROR            ○          ○          ○          ●
YEAR_ERROR              ○          ○          ○          ●
JOURNAL_ERROR           ○          ○          ○          ●
FABRICATED_STATISTIC    ●          ○          ●          ○

● = Primary detection phase
○ = Not detected at this phase
```

### Figure 6: Five-Layer Defense Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    FIVE-LAYER DEFENSE ARCHITECTURE                       │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │ Layer 1: BEHAVIORAL                                              │    │
│  │ ├─ Rules at content generation time                             │    │
│  │ ├─ "Never construct URLs from memory"                           │    │
│  │ └─ Effect: Prevention (reduces fabrication at source)           │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                              ↓                                           │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │ Layer 2: REAL-TIME                                               │    │
│  │ ├─ Post-edit hooks triggered after every file modification      │    │
│  │ ├─ Lightweight verification (DOI format, URL patterns)          │    │
│  │ └─ Effect: Immediate detection (catches errors within seconds)  │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                              ↓                                           │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │ Layer 3: PRE-COMMIT                                              │    │
│  │ ├─ Git pre-commit hooks run validation before commit            │    │
│  │ ├─ Blocks commits containing unverified citations               │    │
│  │ └─ Effect: Batch validation (prevents bad citations in repo)    │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                              ↓                                           │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │ Layer 4: ON-DEMAND                                               │    │
│  │ ├─ Full five-phase pipeline invoked manually or scheduled       │    │
│  │ ├─ Includes human review of content-claim alignment             │    │
│  │ └─ Effect: Deep verification (comprehensive but expensive)      │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                              ↓                                           │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │ Layer 5: REGISTRY                                                │    │
│  │ ├─ Database of verified citations with timestamps               │    │
│  │ ├─ Known-good citations skip re-verification                    │    │
│  │ └─ Effect: Acceleration + audit trail of corrections            │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                                                                          │
│  Defense-in-Depth: Each layer compensates for gaps in others            │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### Figure 7: Proposed Figures for Publication

**Recommended Figures for Journal Submission:**

1. **Panel A:** Sankey diagram showing flow from 150 citations through verification phases to error categories
2. **Panel B:** Stacked bar chart comparing detection rates across methods
3. **Panel C:** Heatmap of error rates by chapter and error type
4. **Panel D:** Example error cases with before/after correction

---

## 6. Conclusion

This study demonstrates that LLM-generated citations exhibit a 46.7% error rate, with the majority of errors (78.6%) undetectable by automated link-checking tools. Our five-phase verification pipeline provides a systematic, reproducible methodology for comprehensive citation verification, while our five-layer defense architecture provides defense-in-depth for production content systems.

### Key Contributions

1. **Five-Phase Verification Pipeline:** Adding Phase 0 (DOI existence validation via CrossRef) before URL resolution distinguishes fabricated DOIs from broken links, improving error categorization and understanding of LLM failure modes.

2. **Five-Layer Defense Architecture:** Post-hoc verification alone is insufficient. Integrating verification at behavioral, real-time, pre-commit, on-demand, and registry layers provides overlapping coverage where each layer compensates for gaps in others.

3. **Error Taxonomy:** Our sixteen-category error taxonomy (FABRICATED_DOI, BROKEN_URL, WRONG_PAPER, CLAIM_MISMATCH, METRIC_ERROR, AUTHOR_ERROR, YEAR_ERROR, JOURNAL_ERROR, FABRICATED_STATISTIC, INVERTED_STATISTICS, FABRICATED_REPOSITORY, GENERIC_URL, CHIMERA_CITATION, BOT_BLOCKED_URL, FINDING_MISREPRESENTATION, TRIAL_IDENTITY_CONFUSION) provides the most comprehensive framework to date for categorizing LLM citation errors. Several categories (CHIMERA_CITATION, FINDING_MISREPRESENTATION, TRIAL_IDENTITY_CONFUSION) represent error types undetectable by any existing automated approach and require multi-factor cross-verification.

4. **Paper-Implementation Alignment Testing:** Cross-corpus validation revealed that automated tooling implemented approximately 2.5 of 5 documented phases (Section 4.6), demonstrating that methodology-implementation drift is itself a verification target requiring automated testing.

5. **Structured Metric Extraction:** The discovery of INVERTED_STATISTICS errors (Section 3.9.4) demonstrates that string-presence checks are insufficient for statistical claims. Metric-value pair extraction and label-value alignment comparison are required for Phase 2 verification of quantitative claims.

### Recommendations

1. **Mandatory citation verification** for all LLM-assisted academic content
2. **Verification integrated into workflows** rather than applied only post-hoc
3. **DOI registry validation** (Phase 0) before URL resolution to catch fabricated DOIs early
4. **Content-level verification** beyond automated link checking
5. **Defense-in-depth** with multiple verification layers
6. **Enhanced journal policies** for manuscripts acknowledging LLM assistance
7. **Paper-code alignment testing** for any published verification methodology with accompanying tooling
8. **Structured metric extraction** replacing keyword/string matching for statistical claim verification
9. **WebSearch escalation** for citations that return "unable to verify" due to paywalls or JavaScript rendering

### Generalizability

While developed for medical content, this methodology is generalizable to any domain with academic citations. The five-phase pipeline detects the same error types regardless of whether citations reference medical journals, legal cases, or policy documents. Only Phase 2 (content-claim alignment) requires domain expertise.

The tools and methodology presented here are freely available for adoption and adaptation by the research community.

---

## 7. Data Availability

The complete verification dataset, error log, and methodology documentation are available:

**Core Documentation:**
- `README.md`: Quick start guide
- `METHODOLOGY.md`: Complete verification protocol (Five-Phase Pipeline + Five-Layer Defense)
- `PAPER.md`: This manuscript

**Supplementary Materials (in `supplementary/` directory):**
- `CORRECTION_LOG.md`: Full error and correction documentation (~70 corrections)
- `PROPOSAL.md`: Research proposal for comparative LLM testing
- `TOOL_INVOCATIONS.md`: Reproducible tool usage examples

**Scripts (in `scripts/` directory):**
- `verification_pipeline.py`: Main verification tool
- `citation_extractor.py`: Citation extraction from markdown
- `doi_validator.py`: CrossRef API validation (Phase 0)
- `url_verifier.py`: URL resolution testing (Phase 1)
- `content_verifier.py`: Content-claim alignment (Phase 2)
- `metadata_verifier.py`: Metadata accuracy verification (Phase 3)

---

## 8. Author Contributions

BT conceived the study, developed the methodology, performed the verification, and wrote the manuscript.

---

## 9. Competing Interests

The author declares no competing interests.

---

## 10. Ethics Statement

This study analyzed citation metadata and publicly available academic content. No human subjects, patient data, or protected health information were involved. The verification methodology evaluates published citations against their source documents using publicly accessible databases (CrossRef, PubMed, publisher websites). All example citations in this manuscript are from published academic literature. IRB review was not required as the study involves analysis of publicly available published materials, not human subjects research.

---

## 11. Acknowledgments

The author thanks the CrossRef and DOI Foundation teams for maintaining the open APIs that make automated citation verification possible.

---

## 12. References

1. Alkaissi H, McFarlane SI. Artificial hallucinations in ChatGPT: implications in scientific writing. Cureus. 2023;15(2):e35179.

2. Walters WH, Wilder EI. Fabrication and errors in the bibliographic citations generated by ChatGPT. Sci Rep. 2023;13(1):14045.

3. Huang J, Tan M. The role of ChatGPT in scientific communication: writing better scientific review articles. Am J Cancer Res. 2023;13(4):1148-1154.

4. Sallam M. ChatGPT utility in healthcare education, research, and practice: systematic review on the promising perspectives and valid concerns. Healthcare. 2023;11(6):887.

5. Thirunavukarasu AJ, Ting DSJ, Elangovan K, et al. Large language models in medicine. Nat Med. 2023;29(8):1930-1940.

6. Lee P, Bubeck S, Petro J. Benefits, limits, and risks of GPT-4 as an AI chatbot for medicine. N Engl J Med. 2023;388(13):1233-1239.

7. Singhal K, Azizi S, Tu T, et al. Large language models encode clinical knowledge. Nature. 2023;620(7972):172-180.

8. Wong A, Otles E, Donnelly JP, et al. External validation of a widely implemented proprietary sepsis prediction model in hospitalized patients. JAMA Intern Med. 2021;181(8):1065-1070.

9. Zech JR, Badgeley MA, Liu M, et al. Variable generalization performance of a deep learning model to detect pneumonia in chest radiographs: a cross-sectional study. PLoS Med. 2018;15(11):e1002683.

10. Obermeyer Z, Powers B, Vogeli C, Mullainathan S. Dissecting racial bias in an algorithm used to manage the health of populations. Science. 2019;366(6464):447-453.

---

## Supplementary Materials

### Supplementary Table S1: Complete Error Log

See `CORRECTION_LOG.md`

### Supplementary Methods S1: Tool Invocation Patterns

See `TOOL_INVOCATIONS.md`

### Supplementary Code S1: Python Implementation

See `scripts/` directory

---

*Manuscript prepared for submission*
*Version: 3.3 (February 24, 2026)*
*Word count: ~14,000*
*Figures: 7*
*Tables: 11*
*References: 10*
