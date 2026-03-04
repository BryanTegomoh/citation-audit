# Citation Verification Methodology for AI-Generated Medical Text

**Version:** 3.3
**Last Updated:** February 24, 2026
**Purpose:** Comprehensive citation verification methodology for LLM-generated content
**Applicability:** Any LLM system generating medical/scientific citations (generalizable to any domain)

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Problem Statement](#problem-statement)
3. [Verification Architecture](#verification-architecture)
4. [Phase 0: DOI Existence Validation](#phase-0-doi-existence-validation)
5. [Phase 1: URL and DOI Resolution Testing](#phase-1-url-and-doi-resolution-testing)
6. [Phase 2: Content-Claim Alignment Verification](#phase-2-content-claim-alignment-verification)
7. [Phase 3: Metadata Accuracy Verification](#phase-3-metadata-accuracy-verification)
8. [Phase 4: Correction and Replacement](#phase-4-correction-and-replacement)
9. [Tools and Methods Used](#tools-and-methods-used)
10. [Error Taxonomy](#error-taxonomy)
11. [Extended Failure Modes (Critical Gaps)](#extended-failure-modes-critical-gaps)
12. [Reproducible Verification Protocol](#reproducible-verification-protocol)
13. [Quality Assurance](#quality-assurance)
14. [Comparative LLM Testing Protocol](#comparative-llm-testing-protocol)
15. [Five-Layer Defense Architecture](#five-layer-defense-architecture)
16. [Automated Hook-Based Implementation](#automated-hook-based-implementation)
17. [Appendices](#appendices)

---

## Executive Summary

This document describes the systematic methodology used to verify and correct citations in a large medical AI handbook. The verification process identified multiple categories of citation errors common in AI-assisted content generation:

- **Broken DOIs/URLs:** Links that return 404 errors or redirect to wrong content
- **Wrong Papers:** Valid DOIs that point to completely different papers than claimed
- **Author Attribution Errors:** Incorrect first author names
- **Year Errors:** Wrong publication years
- **Journal Misattribution:** Correct paper, wrong journal name
- **Claim-Citation Mismatches:** Citation exists and is valid, but does not support the inline claim
- **Fabricated Citations:** Citations that appear valid but do not exist

The methodology combines automated URL testing with manual content verification, achieving complete coverage of all inline citations across 22 chapters.

---

## Problem Statement

### The Challenge of AI-Generated Citations

Large Language Models (LLMs) generate plausible-looking citations that exhibit several failure modes:

1. **Hallucinated DOIs:** DOIs that follow correct format (10.xxxx/...) but do not resolve to any paper
2. **Conflated Citations:** Mixing metadata from multiple papers into one citation
3. **Outdated Information:** Citing papers with old DOIs when newer versions exist
4. **Semantic Drift:** Citations that are topically related but do not support specific claims
5. **Author Transposition:** Citing co-authors as first authors or wrong author entirely

### Why Manual Verification is Required

Automated tools can detect broken URLs but cannot:
- Verify that a paper's content supports the specific claim made
- Detect when a valid DOI points to a wrong paper
- Identify when statistics are misquoted or metrics are reversed
- Recognize when a paper is cited for findings it does not contain

This methodology combines automated link checking with systematic manual content verification.

---

## Verification Architecture

### Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    CITATION VERIFICATION PIPELINE                │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐       │
│  │   PHASE 1    │    │   PHASE 2    │    │   PHASE 3    │       │
│  │  URL/DOI     │───▶│   Content    │───▶│   Metadata   │       │
│  │  Resolution  │    │   Alignment  │    │   Accuracy   │       │
│  └──────────────┘    └──────────────┘    └──────────────┘       │
│         │                   │                   │                │
│         ▼                   ▼                   ▼                │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐       │
│  │   404/Broken │    │    Claim     │    │   Author/    │       │
│  │   Detection  │    │   Mismatch   │    │   Year/DOI   │       │
│  └──────────────┘    └──────────────┘    └──────────────┘       │
│                                                                  │
│                          ▼                                       │
│                  ┌──────────────┐                                │
│                  │   PHASE 4    │                                │
│                  │  Correction  │                                │
│                  │  & Replace   │                                │
│                  └──────────────┘                                │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Input Format

Citations in the source corpus follow this markdown format:
```markdown
([Author et al., Year](https://doi.org/10.xxxx/xxxxx))
```

Example:
```markdown
([Wong et al., 2021](https://doi.org/10.1001/jamainternmed.2021.2626))
```

---

## Phase 0: DOI Existence Validation (NEW)

### Objective
Validate that DOIs exist in the CrossRef registry BEFORE attempting URL resolution. This distinguishes between broken links (transcription errors) and fabricated DOIs (intentional hallucination).

### Method: CrossRef API Query

```python
import aiohttp

async def validate_doi_exists(doi: str) -> dict:
    """Check if DOI exists in CrossRef registry."""
    url = f"https://api.crossref.org/works/{doi}"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                return {"exists": True, "data": await response.json()}
            elif response.status == 404:
                return {"exists": False, "fabricated": True}
            else:
                return {"exists": None, "error": response.status}
```

### Classification

| Response | Interpretation | Action |
|----------|----------------|--------|
| HTTP 200 | DOI exists | Proceed to Phase 1 |
| HTTP 404 | DOI does not exist | Flag as FABRICATED_DOI |
| Other | Unknown | Proceed with caution |

### Why This Phase Matters

**Before Phase 0:** A fabricated DOI like `10.1001/jamanetworkopen.2019.14004` returns 404 at URL resolution and is categorized as "broken link."

**With Phase 0:** The same DOI is recognized as following valid JAMA Network Open format but not existing in CrossRef, indicating intentional fabrication rather than transcription error.

This distinction is critical for understanding LLM failure modes:
- **Transcription errors:** Typos in real DOIs
- **Fabricated DOIs:** Syntactically valid DOIs that were never registered

---

## Phase 1: URL and DOI Resolution Testing

### Objective
Verify that every URL/DOI in the document resolves to an accessible resource.

### Method: WebFetch Tool

The `WebFetch` tool was used to test each URL. This tool:
1. Follows HTTP redirects (301, 302)
2. Returns final destination content
3. Reports HTTP status codes
4. Handles DOI resolution through doi.org

### Execution Protocol

For each citation URL:

```
STEP 1: Extract URL from markdown citation
        Pattern: \[.*?\]\((https?://[^\)]+)\)

STEP 2: Execute WebFetch request
        WebFetch(url=extracted_url, prompt="What is the title and subject of this paper?")

STEP 3: Evaluate response
        - HTTP 200: URL resolves, proceed to Phase 2
        - HTTP 404: BROKEN - flag for replacement
        - HTTP 403: Paywalled - try alternative access methods
        - Redirect: Follow and verify final destination
```

### Example: Detecting Broken DOI

**Input Citation:**
```markdown
([Slight et al., 2013](https://doi.org/10.1007/s40264-013-0089-1))
```

**WebFetch Execution:**
```
Tool: WebFetch
Parameters:
  url: "https://doi.org/10.1007/s40264-013-0089-1"
  prompt: "What is this paper about?"

Result: HTTP 404 - Not Found
```

**Conclusion:** DOI is broken/invalid. Requires replacement.

### Example: Detecting Wrong Paper via Redirect

**Input Citation:**
```markdown
([Zhao et al., 2019](https://doi.org/10.1016/j.eswa.2019.02.008))
```

**WebFetch Execution:**
```
Tool: WebFetch
Parameters:
  url: "https://doi.org/10.1016/j.eswa.2019.02.008"
  prompt: "What is this paper about?"

Result:
  Status: 302 Redirect
  Final URL: https://linkinghub.elsevier.com/retrieve/pii/S0957417419301071
  Content Title: "A multi-agent dynamic system for robust multi-face tracking"
```

**Analysis:** The DOI resolves but to a paper about FACE TRACKING, not fetal heart rate analysis as claimed in the text.

**Conclusion:** WRONG PAPER - valid DOI pointing to incorrect content.

### DOI Resolution Patterns

DOIs follow predictable redirect patterns:

| DOI Prefix | Publisher | Redirect Host |
|------------|-----------|---------------|
| 10.1001/ | JAMA Network | jamanetwork.com |
| 10.1016/ | Elsevier | linkinghub.elsevier.com |
| 10.1038/ | Nature | nature.com |
| 10.1093/ | Oxford Academic | academic.oup.com |
| 10.1056/ | NEJM | nejm.org |
| 10.1136/ | BMJ | bmj.com |
| 10.1186/ | BioMed Central | biomedcentral.com |
| 10.1371/ | PLOS | journals.plos.org |
| 10.1128/ | ASM | journals.asm.org |
| 10.1017/ | Cambridge | cambridge.org |

---

## Phase 2: Content-Claim Alignment Verification

### Objective
Verify that the cited paper actually supports the specific claim made in the text.

### Method: Contextual Content Analysis

For each citation that passed Phase 1, extract:
1. The inline claim (text immediately before/after the citation)
2. The actual content of the cited paper

### Extraction Protocol

```
STEP 1: Read source file
        Tool: Read(file_path)

STEP 2: Locate citation in context
        Extract 200 characters before and after citation link

STEP 3: Identify the specific claim
        - Statistics cited (percentages, p-values, sample sizes)
        - Findings attributed (e.g., "showed 35% reduction")
        - Conclusions claimed (e.g., "demonstrated that...")

STEP 4: Fetch paper content
        Tool: WebFetch(url, prompt="What are the main findings?")
        OR
        Tool: WebSearch(query="[Author] [Topic] [Year] findings")

STEP 5: Compare claim to actual findings
        - Do the numbers match?
        - Does the paper actually make this conclusion?
        - Is the claim a reasonable summary of the paper?
```

### Example: Detecting Claim-Citation Mismatch

**Inline Text:**
```markdown
- [The Epic Sepsis Model, widely deployed, showed 33% sensitivity and 67% specificity]
  ([Wong et al., 2021](https://doi.org/10.1001/jamainternmed.2021.2626))
```

**Claim Extracted:**
- Sensitivity: 33%
- Specificity: 67%

**WebFetch Verification:**
```
Tool: WebFetch
Parameters:
  url: "https://doi.org/10.1001/jamainternmed.2021.2626"
  prompt: "What sensitivity and specificity did the Epic Sepsis Model achieve?"

Result:
  Sensitivity: 33% (CORRECT)
  Specificity: 83% (INCORRECT - text said 67%)
```

**Conclusion:** Specificity value is wrong. Text states 67%, paper reports 83%.

**Correction Applied:**
```markdown
- [The Epic Sepsis Model, widely deployed, showed 33% sensitivity and 83% specificity]
  ([Wong et al., 2021](https://doi.org/10.1001/jamainternmed.2021.2626))
```

### Example: Detecting Complete Claim Mismatch

**Inline Text:**
```markdown
Studies from India found regional disparities in recommendations
([Somashekhar et al., 2018](https://doi.org/10.1093/annonc/mdy144))
```

**Claim Extracted:** "regional disparities in recommendations"

**WebSearch Verification:**
```
Tool: WebSearch
Parameters:
  query: "Somashekhar Watson oncology India 2018 findings"

Result:
  Paper finding: 93% concordance between Watson and tumor board
  This indicates HIGH AGREEMENT, not "regional disparities"
```

**Analysis:** The paper shows Watson worked WELL in India with 93% concordance. The claim suggests it showed problems/disparities, which is the opposite of what the paper found.

**Conclusion:** CLAIM-CITATION MISMATCH - citation does not support the claim.

---

## Phase 3: Metadata Accuracy Verification

### Objective
Verify that citation metadata (author, year, journal) is accurate.

### Verification Elements

| Element | Verification Method |
|---------|---------------------|
| First Author | Compare to paper's author list |
| Publication Year | Check paper metadata |
| Journal Name | Verify from DOI landing page |
| DOI Format | Validate DOI syntax |

### Method: Cross-Reference Search

```
Tool: WebSearch
Parameters:
  query: "[First Author] [Topic Keywords] [Year] journal"

Purpose: Independently verify paper existence and metadata
```

### Example: Detecting Wrong Author Attribution

**Input Citation:**
```markdown
([Arnal et al., 2021](https://pubmed.ncbi.nlm.nih.gov/34047244/))
```

**WebFetch Verification:**
```
Tool: WebFetch
Parameters:
  url: "https://pubmed.ncbi.nlm.nih.gov/34047244/"
  prompt: "Who are the authors of this paper?"

Result:
  Authors: M Botta, E F E Wenstedt, A M Tsonas, L A Buiteman-Kruizinga...
  First Author: M Botta (NOT Arnal)
```

**Conclusion:** Wrong author attribution. Should be "Botta et al., 2021"

**Correction Applied:**
```markdown
([Botta et al., 2021](https://doi.org/10.1080/17476348.2021.1953979))
```

### Example: Detecting Wrong Year

**Input Citation:**
```markdown
([Tschandl et al., 2020](https://doi.org/10.1016/S1470-2045(19)30333-X))
```

**Analysis of DOI:**
- DOI contains "(19)" suggesting 2019, not 2020
- Journal: Lancet Oncology (S1470-2045)

**WebSearch Verification:**
```
Tool: WebSearch
Parameters:
  query: "Tschandl Lancet Oncology 2019 skin lesion classification"

Result:
  Publication date: July 2019
  Title: "Comparison of the accuracy of human readers versus
         machine-learning algorithms for pigmented skin lesion classification"
```

**Conclusion:** Wrong year. Paper was published in 2019, not 2020.

**Correction Applied:**
```markdown
([Tschandl et al., 2019](https://doi.org/10.1016/S1470-2045(19)30333-X))
```

---

## Phase 4: Correction and Replacement

### Objective
For each identified error, find the correct citation or rephrase the claim.

### Decision Tree

```
                    ┌─────────────────┐
                    │  Error Type?    │
                    └────────┬────────┘
                             │
        ┌────────────────────┼────────────────────┐
        ▼                    ▼                    ▼
  ┌───────────┐       ┌───────────┐       ┌───────────┐
  │  Broken   │       │   Wrong   │       │   Claim   │
  │   DOI     │       │   Paper   │       │  Mismatch │
  └─────┬─────┘       └─────┬─────┘       └─────┬─────┘
        │                   │                   │
        ▼                   ▼                   ▼
  ┌───────────┐       ┌───────────┐       ┌───────────┐
  │  Search   │       │  Search   │       │  Option A │
  │  for      │       │  for      │       │  Find new │
  │  correct  │       │  paper    │       │  citation │
  │  DOI      │       │  matching │       │           │
  └───────────┘       │  claim    │       │  Option B │
                      └───────────┘       │  Rephrase │
                                          │  claim    │
                                          └───────────┘
```

### Method: Finding Correct Citations

```
Tool: WebSearch
Parameters:
  query: "[Topic] [Specific finding] [Year range] DOI"

Example:
  query: "fetal heart rate CTG machine learning classification 2019 DOI BMC"

Process:
  1. Search for papers matching the claimed topic
  2. Verify the paper contains the specific finding
  3. Extract correct DOI, author, year, journal
  4. Apply correction to source file
```

### Example: Finding Replacement for Broken DOI

**Original (Broken):**
```markdown
([Green et al., 2019](https://doi.org/10.1001/jamanetworkopen.2019.14004))
```
Claim: "35% reduction in cardiac arrests outside ICU"

**Search Process:**
```
Tool: WebSearch
Parameters:
  query: "University of Michigan deterioration index cardiac arrest reduction 2019"

Result: No peer-reviewed paper found supporting this specific claim
```

**Resolution:** Remove unverifiable claim, replace with general statement:
```markdown
Hospital implementations have reported reductions in care escalations
and improved identification of deteriorating patients
```

### Method: Applying Corrections

```
Tool: Edit
Parameters:
  file_path: [path to source file]
  old_string: [original incorrect citation]
  new_string: [corrected citation]
```

**Example:**
```
Tool: Edit
Parameters:
  file_path: "specialties/critical-care.md"
  old_string: "([Arnal et al., 2021](https://pubmed.ncbi.nlm.nih.gov/34047244/))"
  new_string: "([Botta et al., 2021](https://doi.org/10.1080/17476348.2021.1953979))"
```

---

## Tools and Methods Used

### Primary Tools

| Tool | Purpose | When Used |
|------|---------|-----------|
| **Read** | Extract file contents | Initial file analysis |
| **WebFetch** | Test URL resolution, fetch content | Phase 1, Phase 2 |
| **WebSearch** | Find correct papers, verify metadata | Phase 2, Phase 3, Phase 4 |
| **Edit** | Apply corrections | Phase 4 |
| **Grep** | Find all instances of a citation | Cross-file verification |
| **Glob** | Locate all source files | Initial scoping |

### WebFetch Usage Patterns

**Pattern 1: DOI Resolution Test**
```
WebFetch(
  url="https://doi.org/10.xxxx/xxxxx",
  prompt="What is the title of this paper?"
)
```

**Pattern 2: Content Extraction**
```
WebFetch(
  url="https://doi.org/10.xxxx/xxxxx",
  prompt="What are the main findings? What sensitivity/specificity
         values are reported?"
)
```

**Pattern 3: Author Verification**
```
WebFetch(
  url="https://pubmed.ncbi.nlm.nih.gov/PMID/",
  prompt="Who are the authors of this paper? What is the title?"
)
```

### WebSearch Usage Patterns

**Pattern 1: Find Correct Paper**
```
WebSearch(
  query="[Topic] [Specific metric] [Year] journal DOI"
)
```

**Pattern 2: Verify Paper Exists**
```
WebSearch(
  query="[Author] [Journal] [Year] [Topic]"
)
```

**Pattern 3: Find Alternative Source**
```
WebSearch(
  query="[Claim being made] systematic review meta-analysis"
)
```

### Parallel Agent Deployment

For efficiency, verification was parallelized across chapters:

```
Deploy agents in parallel:
  Agent 1: Verify chapter-1.md
  Agent 2: Verify chapter-2.md
  Agent 3: Verify chapter-3.md
  ...
  Agent N: Verify chapter-N.md

Each agent executes full Phase 1-4 pipeline independently
Results aggregated and cross-checked
```

---

## Error Taxonomy

### Category 1: Broken URLs (404 Errors)

**Characteristics:**
- DOI does not resolve
- URL returns HTTP 404
- Domain no longer exists

**Detection Method:** WebFetch returns error status

**Example:**
```
DOI: 10.1007/s40264-013-0089-1
Status: 404 Not Found
```

**Resolution:** Search for correct DOI or alternative source

### Category 2: Wrong Paper (Valid DOI, Wrong Content)

**Characteristics:**
- DOI resolves successfully
- Paper exists
- Paper topic completely different from claim

**Detection Method:** WebFetch content analysis

**Example:**
```
Claimed: Fetal heart rate analysis
Actual: Multi-face tracking algorithm
```

**Resolution:** Find paper that actually matches the topic

### Category 3: Author Attribution Error

**Characteristics:**
- Paper is correct
- First author name is wrong

**Detection Method:** WebFetch author list extraction

**Example:**
```
Cited as: Arnal et al.
Actual first author: Botta
```

**Resolution:** Correct author name in citation

### Category 4: Year Error

**Characteristics:**
- Paper is correct
- Publication year is wrong

**Detection Method:** DOI pattern analysis, WebSearch verification

**Example:**
```
Cited as: 2020
Actual: 2019 (DOI contains "19")
```

**Resolution:** Correct year in citation

### Category 5: Journal Misattribution

**Characteristics:**
- Paper is correct
- Journal name is wrong

**Detection Method:** Cross-reference with publisher metadata

**Example:**
```
Cited as: JAMA Internal Medicine
Actual: NEJM
```

**Resolution:** Correct journal name or remove if mentioned

### Category 6: Claim-Citation Mismatch

**Characteristics:**
- Paper exists and is valid
- Paper does not support the specific claim made

**Detection Method:** Manual content comparison

**Example:**
```
Claim: "showed regional disparities"
Paper finding: "93% concordance" (opposite meaning)
```

**Resolution:** Either find supporting citation or rephrase claim

### Category 7: Metric Error

**Characteristics:**
- Paper is correct
- Specific numbers are wrong

**Detection Method:** Extract metrics from paper, compare to text

**Example:**
```
Text claims: 67% specificity
Paper reports: 83% specificity
```

**Resolution:** Correct the metric in text

### Category 8: Fabricated Citation

**Characteristics:**
- Author name may or may not exist
- Claimed paper does not exist
- No trace found via any search

**Detection Method:** Exhaustive search failure

**Example:**
```
Cited: Green et al., 2019, JAMA Network Open
Search result: No such paper exists
```

**Resolution:** Remove claim or find legitimate source

### Category 9: Syntactically Valid Non-Existent DOI (NEW)

**Characteristics:**
- DOI follows correct publisher format (e.g., `10.1001/jamanetworkopen.2019.XXXXX`)
- DOI does not exist in CrossRef registry
- Indicates intentional fabrication rather than typo

**Detection Method:** Phase 0 CrossRef API validation

**Example:**
```
DOI: 10.1001/jamanetworkopen.2019.14004
CrossRef API: 404 (does not exist)
Analysis: Valid JAMA format but not registered
```

**Resolution:** Flag as fabricated, search for real paper supporting claim

### Category 10: Fabricated Statistic (NEW)

**Characteristics:**
- Specific numbers cited (percentages, sample sizes, p-values)
- No verifiable source exists
- Often accompanies fabricated citation

**Detection Method:** Citation fails + claim contains specific statistic

**Example:**
```
Claim: "35% reduction in cardiac arrests"
Citation: Non-existent DOI
Analysis: Statistic itself may be fabricated
```

**Resolution:** Either find alternative source OR remove specific claim

---

## Extended Failure Modes (Critical Gaps)

Through iterative application, nine critical failure modes were identified that extend beyond traditional verification:

### Gap 1: Syntactically Valid but Non-Existent DOIs
- DOI follows correct format but doesn't exist
- Phase 0 catches this; standard Phase 1 only reports "broken URL"
- **Detection:** CrossRef API query before URL fetch

### Gap 2: Claim Specificity Without Source
- Highly specific claims (exact %, specific institutions) with no source
- When URL fails, the fabricated statistic isn't explicitly flagged
- **Detection:** Parse claims for specificity, escalate when citation fails

### Gap 3: Pre-Generation Verification Gap
- Citations verified only post-hoc, not during generation
- Root cause of all errors: no verification at generation time
- **Detection:** N/A (workflow integration needed)

### Gap 4: Paywalled Content Extraction Failure
- URL resolves but content extraction fails (paywall, JavaScript, bot blocking)
- Categorized as "unable to verify" and deprioritized
- **Detection:** Require 20% manual sampling of "unable to verify"

### Gap 5: Cross-File Synchronization
- Same error in multiple files; correction doesn't propagate
- Pipeline processes files independently
- **Detection:** Post-correction grep verification:
  ```bash
  grep -r "OLD_DOI_PATTERN" --include="*.md" --include="*.qmd"
  ```

### Gap 6: Confidence Calibration
- Content alignment scores not calibrated against actual error rates
- 0.6 confidence "aligned" may still be wrong
- **Detection:** Track scores vs. ground truth, establish thresholds

### Gap 7: Fabricated Experiential Claims
- Anecdotal claims without citations ("At University X...")
- Not citation errors but content fabrication
- **Detection:** Flag uncited institutional claims for verification

### Gap 8: Scaling Human Review
- Phase 2 requires human judgment; bottleneck at scale
- 1,000+ citations becomes impractical
- **Detection:** Stratified sampling, prioritize high-specificity claims

### Gap 9: DOI Existence Validation Timing
- CrossRef query happens in Phase 3, AFTER Phase 1 passes
- Non-existent DOIs should be caught earlier
- **Detection:** Reorder pipeline (Phase 0 before Phase 1)

### Gap 10: URL Construction from Memory (Pre-Generation Failure)
- URLs constructed from LLM memory based on pattern recognition, not extracted from search results
- Hooks verify URLs POST-HOC but cannot distinguish memory-constructed vs. search-extracted URLs
- Government websites frequently archive content to new domains (e.g., whitehouse.gov → bidenwhitehouse.archives.gov)
- A syntactically valid URL that returns 404 is indistinguishable from a typo until verification runs

**Detection:** Cannot be detected by automated hooks. Requires pre-generation behavioral rule:
- NEVER construct URLs from memory
- URLs must be extracted from WebSearch results or explicitly provided by user
- When uncertain, search first: `WebSearch("[Organization] [Topic]")` then extract exact URL

**Example Failure:**
```
Memory-constructed: https://www.whitehouse.gov/ostp/news-updates/2023/07/21/...
Actual location: https://bidenwhitehouse.archives.gov/briefing-room/statements-releases/2023/07/21/...
```
The LLM "knows" White House announcements follow a pattern but doesn't know the content was archived. WebSearch would have returned the correct archived URL.

**Enforcement:** CLAUDE.md Pre-Edit Protocol, not hooks. Hooks run after the edit; the rule must be followed during generation.

### Gap 11: Cross-File Attribution Inconsistency

**Pattern:** The same fact, quote, or institutional claim is attributed to different people across different files in the same project. Each citation passes independent verification, but cross-file comparison reveals conflicting attributions.

**Example (February 5, 2026):** An AMA statement about AI prescribing was attributed to "Dr. Bobby Mukkamala, AMA Board Chair" in one chapter but to "AMA CEO Dr. John Whyte" in another. Investigation revealed Whyte became AMA CEO in July 2025, making the Mukkamala attribution stale.

**Detection:** After per-file verification, run cross-file comparison:
```bash
grep -rn "AMA\|CEO\|Board Chair\|Director" --include="*.md" --include="*.qmd" | sort
```
Group by topic and verify consistent attribution across all instances.

### Gap 12: Post-Verification Regression

**Pattern:** A previously verified and corrected citation is re-broken by a subsequent edit. The correction log shows the fix was applied, but a later session introduced a new error at the same location.

**Example (February 5, 2026):** January 18 verification corrected "Arnal et al." to "Botta et al." in a critical care chapter. The replacement DOI suffix (`1953979`) was incorrect (returns 404). Correct suffix: `1933450`. First fix was partially correct (right author, wrong DOI).

**Detection:**
1. Re-verify corrected citations through Phase 0-1 immediately after correction
2. Flag previously-corrected citations for mandatory re-verification in future passes
3. Track correction lineage: citations corrected once have higher regression risk

### Gap 13: Journal-Publisher Mismatch (DOI Prefix Validation)

**Pattern:** DOI prefix identifies one publisher, but citation text claims a journal from a different publisher. Often caused by confusing research institution with publication venue, or mixing up journals from different publishers.

**Examples (February 5, 2026):**
- Galloway et al. 2019: Cited as Mayo Clinic Proceedings (`10.1016/...`, Elsevier) but published in JAMA Cardiology (`10.1001/...`, AMA)
- Freeman et al. 2020: Cited with JAMA Dermatology DOI (`10.1001/...`) but published in BMJ (`10.1136/...`)

**Detection:** Add DOI prefix-to-publisher validation between Phase 0 and Phase 1:
```python
def check_prefix_journal_alignment(doi, claimed_journal):
    prefix = doi.split("/")[0]
    expected_publisher = PUBLISHER_PREFIXES.get(prefix)
    if expected_publisher and claimed_journal not in expected_publisher:
        flag("PREFIX_JOURNAL_MISMATCH")
```

See `data/publisher_prefixes.json` for the complete prefix mapping (90+ publishers).

### Gap 14: Fabricated Code Repositories

**Pattern:** LLMs generate plausible GitHub URLs for tools, frameworks, or assessment instruments that do not exist. URLs follow correct GitHub patterns but the repositories have never existed.

**Detection:** Add repository-specific verification between Phase 1 and Phase 2:
```python
def verify_repository(url):
    if 'github.com' in url:
        api_url = url.replace('github.com', 'api.github.com/repos')
        response = requests.get(api_url)
        if response.status_code == 404:
            return "FABRICATED_REPOSITORY"
```

### Gap 15: Generic URL Resolution (Specific-to-General Drift)

**Pattern:** Citation references a specific document, but URL resolves to a top-level landing page. HTTP 200 passes Phase 1, but the destination lacks the specific content referenced.

**Detection:** Compare URL specificity to citation specificity. Check whether document identifiers (e.g., "MDCG 2019-11", "ISO 14971") from citation text appear in the page content.

### Gap 16: Paper-Implementation Alignment Drift

**Pattern:** Paper documents a methodology but implementing scripts do not fully implement the documented methodology. Over time, paper and scripts diverge.

**Detection:** Implement paper-code alignment test suite that verifies all documented phases are invocable, all error categories are detectable, and documented thresholds match implementation values.

### Gap 17: Chimera Citation Pattern

**Discovered:** February 2026.

**Pattern:** The LLM constructs a citation by harvesting verified components from a real paper (author, statistics, affiliation) and assembling them into a non-existent publication with a fabricated venue, DOI, and elaborated findings.

**Why existing defenses fail:** Author verification passes, statistics verification passes, institutional verification passes, topic alignment passes, DOI format passes. Each single-factor check succeeds; only multi-factor cross-verification (DOI resolves to paper with claimed author AND claimed venue) detects the chimera.

**Detection:** After confirming author and statistics independently, verify the specific DOI resolves to a page containing both the claimed author AND the claimed statistics in the same document.

### Gap 18: Fabrication Propagation with Escalating Detail

**Discovered:** February 2026.

**Pattern:** When a fabricated citation appears in one file and is later referenced in another file, the LLM generates increasingly elaborate fabricated detail. Each successive mention adds specificity (structured tables, named frameworks, precise percentage breakdowns) that makes the fabrication appear more thoroughly researched.

**Detection:** After identifying any fabricated citation, grep for all instances across the entire corpus. Compare detail levels across files. If later instances contain substantially more specific claims, treat additional detail as fabricated unless independently verified.

**Implication:** Citation audits must be cross-file, not per-file.

### Gap 19: Government Database Bot-Blocking False Positives

**Discovered:** February 2026.

**Pattern:** Government databases (FDA accessdata.fda.gov, NIH databases, EU regulatory portals) return HTTP 403/404 to automated verification requests while remaining accessible to human users in browsers. The citation is valid but automated Phase 1 verification flags it as broken.

**Detection:** Add a government domain allowlist that triggers alternative verification (WebSearch for document identifiers) when standard HTTP checks fail. Classify as BOT_BLOCKED_URL rather than BROKEN_URL.

**Implication:** False positives from bot-blocked sites inflate apparent broken URL rates. Reports should distinguish BROKEN_URL from BOT_BLOCKED_URL.

### Gap 20: Same-Topic Qualitative Finding Misrepresentation

**Discovered:** February 2026.

**Pattern:** Correct paper cited for correct topic, but the specific qualitative finding (direction of effect) is wrong. Unlike INVERTED_STATISTICS (Gap 13), this involves misrepresenting conclusions rather than swapping numerical values.

**Detection:** Extend Phase 2 to include directional claim extraction (positive/negative/neutral effect) and compare against the paper's actual conclusion.

**Distinction from related gaps:**
- Gap 3 (CLAIM_MISMATCH): Paper and claim are on different topics
- Gap 13 (INVERTED_STATISTICS): Numerical values swapped between labels
- Gap 20: Same topic, but qualitative finding misrepresented

### Gap 21: Trial and Study Identity Confusion

**Discovered:** February 2026.

**Pattern:** Distinct clinical trials by the same investigator are conflated. Statistics from Study A are attributed to Study B because both share the same first author and topic area.

**Detection:** When Phase 2 identifies statistical claims that do not match the resolved paper but are topically aligned, search for other publications by the same first author on the same topic.

**Distinction from Gap 17 (CHIMERA_CITATION):** Chimeras combine a real paper with a fabricated venue. Trial confusion conflates two real papers. All components are individually verifiable; the error is misattribution, not fabrication.

---

## Reproducible Verification Protocol

### Prerequisites

1. Access to WebFetch tool (URL fetching with content extraction)
2. Access to WebSearch tool (academic search capability)
3. Access to file Read/Edit tools
4. Medical/scientific domain knowledge for claim evaluation

### Step-by-Step Protocol

#### Step 1: Extract All Citations

```bash
# Pattern to extract markdown citations
grep -oP '\[([^\]]+)\]\((https?://[^\)]+)\)' file.md
```

**Output format:**
```
[Wong et al., 2021](https://doi.org/10.1001/jamainternmed.2021.2626)
[Bates et al., 2003](https://doi.org/10.1001/jama.289.9.1107)
...
```

#### Step 2: Test Each URL

For each extracted URL:

```
INPUT: url
EXECUTE: WebFetch(url, "What is the title and main finding?")
OUTPUT: {status, title, content_summary}

IF status == 404:
    FLAG as BROKEN
ELSE IF status == 200:
    PROCEED to Step 3
ELSE IF status == 302:
    FOLLOW redirect, re-evaluate
```

#### Step 3: Extract Inline Claim

```
INPUT: citation_location in file
EXECUTE: Read surrounding 500 characters
OUTPUT: claim_text

PARSE claim_text for:
  - Statistics (numbers, percentages)
  - Findings ("showed", "demonstrated", "found")
  - Conclusions ("therefore", "indicating")
```

#### Step 4: Verify Claim Against Paper

```
INPUT: claim_text, paper_content
EXECUTE: Compare claim to paper findings

CHECK:
  - Do statistics match?
  - Does paper make this conclusion?
  - Is attribution accurate?

OUTPUT: {match: boolean, discrepancy: string}
```

#### Step 5: Verify Metadata

```
INPUT: citation (author, year, journal)
EXECUTE:
  WebSearch("[Author] [Topic] [Year] journal")
  WebFetch(url) for author list

COMPARE:
  - First author matches?
  - Year matches?
  - Journal matches?

OUTPUT: {metadata_correct: boolean, corrections: object}
```

#### Step 6: Apply Corrections

```
IF broken_url:
    correct_url = WebSearch for replacement
    Edit(file, old_citation, new_citation)

IF wrong_paper:
    correct_paper = WebSearch for topic match
    Edit(file, old_citation, new_citation)

IF claim_mismatch:
    EITHER find_new_citation
    OR rephrase_claim
    Edit(file, old_text, new_text)

IF metadata_error:
    Edit(file, old_citation, corrected_citation)
```

#### Step 7: Verification Pass

```
FOR each correction:
    Re-execute WebFetch on new URL
    Verify new citation supports claim
    Confirm metadata accuracy
```

---

## Quality Assurance

### Cross-Verification Checks

1. **URL Retest:** After correction, WebFetch the new URL to confirm resolution
2. **Claim Re-check:** Verify corrected citation supports the claim
3. **Cross-file Consistency:** Grep for same citation across all files, ensure consistent correction
4. **Metadata Validation:** Confirm author/year/journal match paper metadata

### Common Pitfalls

| Pitfall | Prevention |
|---------|------------|
| Accepting first search result | Verify content matches specific claim |
| Trusting DOI format validity | Always test resolution |
| Assuming co-authors are first authors | Check actual author order |
| Conflating similar papers | Verify exact title and DOI |
| Missing multiple instances | Grep across all files |

### Documentation Requirements

For each correction, document:
1. Original citation (verbatim)
2. Error type identified
3. Verification method used
4. Search queries executed
5. New citation (verbatim)
6. Verification of correction

---

## Appendices

### Appendix A: Error Rate by Category

| Error Category | Count | Percentage |
|---------------|-------|------------|
| Broken DOI/URL | 15 | 21% |
| Wrong Paper | 18 | 26% |
| Author Error | 8 | 11% |
| Year Error | 9 | 13% |
| Journal Error | 7 | 10% |
| Claim Mismatch | 7 | 10% |
| Metric Error | 6 | 9% |
| **Total** | **70** | **100%** |

### Appendix B: Source Corpus Structure

**Part 1: Foundations (3 chapters)**
- History of AI in Medicine
- AI/ML Fundamentals
- Clinical Data Foundations

**Part 2: Medical Specialties (19 chapters)**
- Radiology, Internal Medicine, Surgery, Pediatrics, Emergency Medicine, Cardiology, OB/GYN, Critical Care, Oncology, Neurology, Psychiatry, Primary Care, Pathology, Dermatology, Ophthalmology, Orthopedics, Infectious Diseases, Allergy/Immunology/Genetics, Surgical Subspecialties

### Appendix C: Tool Invocation Examples

See `TOOL_INVOCATIONS.md` for complete examples of each tool usage pattern.

### Appendix D: Correction Log

See `CORRECTION_LOG.md` for detailed log of every correction applied.

---

---

## Comparative LLM Testing Protocol

This methodology enables systematic comparison of citation accuracy across different LLM systems.

### Target Systems

| System | Type | Expected Use Case |
|--------|------|-------------------|
| OpenEvidence | Medical-specialized | Clinical decision support |
| Doximity GPT | Medical-specialized | Physician-facing queries |
| ChatGPT/GPT-4 | General-purpose | Medical content drafting |
| Claude | General-purpose | Research assistance |
| Grok | General-purpose | Real-time information |
| Gemini | General-purpose | Multimodal queries |
| Perplexity | Search-augmented | Citation-focused responses |

### Standardized Query Set

Create 10-20 medical queries requiring cited responses:

**Foundational Questions (well-documented topics):**
1. What is the evidence base for AI in radiology?
2. What are the key validation studies for clinical decision support systems?
3. How accurate are AI sepsis prediction models?

**Specialized Questions (domain-specific):**
1. What is the evidence for AI in fetal heart rate monitoring?
2. What studies support AI-assisted endoscopy?
3. How has AI performed in psychiatric diagnosis?

**Statistical Questions (requiring specific numbers):**
1. What sensitivity/specificity do AI chest X-ray models achieve?
2. What are reported accuracy rates for AI in dermatology?
3. What sample sizes have been used in AI validation studies?

### Collection Protocol

1. Query each system with identical prompts
2. Request explicit citations in responses
3. Record complete response including all URLs/DOIs
4. Note timestamp and any system-specific formatting

### Verification Protocol

Apply the five-phase pipeline (0-4) to all citations from all systems:
- Phase 0: DOI existence validation
- Phase 1: URL resolution
- Phase 2: Content-claim alignment
- Phase 3: Metadata accuracy
- Phase 4: Correction (for analysis, not publication)

### Metrics

| Metric | Definition |
|--------|------------|
| Total Error Rate | Errors / Total citations |
| Fabrication Rate | Non-existent citations / Total |
| Specificity Accuracy | Correct specific statistics / Claimed statistics |
| Content Match Rate | Papers supporting claims / Resolving URLs |

### Analysis

Compare across systems:
- Overall error rates
- Error type distribution
- Performance on foundational vs. specialized content
- Fabrication patterns (random vs. systematic)

---

## Five-Layer Defense Architecture

### Overview

Citation verification is most effective when implemented as a **defense-in-depth** system with multiple layers. Each layer catches different error types at different points in the workflow.

### The Five Layers

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       FIVE-LAYER CITATION DEFENSE                            │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  Layer 1          Layer 2          Layer 3          Layer 4          Layer 5│
│  BEHAVIORAL       REAL-TIME        PRE-COMMIT       ON-DEMAND       REGISTRY│
│  (CLAUDE.md)      (PostToolUse)    (validate.py)    (/verify)       (JSON)  │
│                                                                              │
│  ┌─────────┐      ┌─────────┐      ┌─────────┐      ┌─────────┐    ┌──────┐│
│  │PREVENT  │  →   │ DETECT  │  →   │  GATE   │  →   │  DEEP   │ ←  │KNOWN ││
│  │at gen   │      │ after   │      │ before  │      │  CHECK  │    │GOOD  ││
│  │time     │      │ edit    │      │ commit  │      │         │    │      ││
│  └─────────┘      └─────────┘      └─────────┘      └─────────┘    └──────┘│
│       │                │                │                │              │   │
│       ▼                ▼                ▼                ▼              ▼   │
│  Never construct  Format checks     Batch DOI        Full 5-phase   Skip   │
│  URLs from        URL syntax        validation       pipeline       verified│
│  memory           Stats warnings    Registry match   Corrections    cites  │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Layer 1: Behavioral Prevention (CLAUDE.md)

**Purpose:** Prevent citation errors at generation time

**Implementation:** Rules in CLAUDE.md that govern how citations are created

**Key Rules:**
- NEVER construct URLs from memory
- URLs must come from WebSearch results or user-provided sources
- WebSearch to verify source exists before adding citation
- Verify claim matches source before writing

**Why This Layer Matters:**
Post-hoc verification (Layers 2-4) can detect errors but cannot determine whether a URL was extracted from search results vs. constructed from memory. The behavioral layer prevents errors before they occur.

### Layer 2: Real-Time Detection (PostToolUse Hook)

**Purpose:** Immediate feedback after every edit

**File:** `~/.claude/hooks/verify-citations-light.py`

**Characteristics:**
- Runs after every Edit/Write on source files
- No network calls (<100ms)
- Non-blocking warnings

**Checks:**
- DOI format validity
- Placeholder DOI patterns (10.xxxx)
- URL syntax errors
- Statistics without adjacent citations
- Duplicate URLs in same edit
- Citations in verified registry (skip further checks)

### Layer 3: Pre-Commit Validation (validate_content.py)

**Purpose:** Quality gate before code is committed

**File:** `scripts/validate_content.py` (function: `check_unverified_citations`)

**Characteristics:**
- Runs during pre-commit hook
- Checks against verified-citations.json registry
- Flags new citations for verification

**Integration:**
```python
def check_unverified_citations(file_path: str) -> List[str]:
    """Check for citations not in verified registry."""
    registry = load_verified_citations()
    citations = extract_citations(file_path)

    for citation in citations:
        if not is_in_registry(citation, registry):
            warnings.append(f"Unverified citation: {citation}")

    return warnings
```

### Layer 4: On-Demand Deep Verification (/verify-chapter Skill)

**Purpose:** Comprehensive verification when needed

**Invocation:** `/verify-chapter` skill or manual pipeline run

**Characteristics:**
- Full 5-phase pipeline
- Network calls to CrossRef, publishers
- Correction suggestions
- Adds verified citations to registry

### Layer 5: Verified Citations Registry

**Purpose:** Known-good whitelist to skip redundant verification

**File:** `citations/verified-citations.json`

**Schema:**
```json
{
  "_metadata": {
    "description": "Registry of verified citations",
    "last_updated": "2026-01-29",
    "verification_protocol": "CLAUDE.md Citation Generation Protocol"
  },
  "citations": [
    {
      "doi": "10.1001/jamainternmed.2021.2626",
      "url": "https://doi.org/10.1001/jamainternmed.2021.2626",
      "first_author": "Andrew Wong",
      "year": "2021",
      "title": "External Validation of a Widely Implemented Proprietary Sepsis Prediction Model",
      "journal": "JAMA Internal Medicine",
      "verified_date": "2026-01-18",
      "claim_context": "Epic Sepsis Model validation - 33% sensitivity, 83% specificity"
    }
  ],
  "_known_errors": {
    "description": "Audit trail of discovered and corrected errors",
    "errors": []
  }
}
```

### Author Matching Implementation Detail

**Problem Discovered:** Citation text uses last names ("Wong et al.") but registry may store full names ("Andrew Wong"). Simple string matching fails.

**Solution:** Store ALL name parts from the author field and match against any part:

```python
def build_author_set(citation):
    """Store all name parts for flexible matching."""
    authors = set()
    if citation.get("first_author"):
        # "Andrew Wong" → {"andrew", "wong"}
        for name_part in citation["first_author"].lower().split():
            authors.add(name_part)
    return authors

def matches_registry(text_author, registry_entry):
    """Check if extracted author matches registry."""
    text_parts = text_author.lower().replace("et al", "").strip().split()
    registry_parts = build_author_set(registry_entry)
    return any(part in registry_parts for part in text_parts)
```

This ensures "Wong et al." matches registry entry "Andrew Wong".

---

## Automated Hook-Based Implementation

### Overview

The five-phase verification pipeline has been implemented as automated hooks that run during content editing sessions. This ensures verification happens automatically rather than requiring manual invocation.

### Architecture: Three-Tier Runtime Verification

```
┌─────────────────────────────────────────────────────────────────┐
│                 AUTOMATED VERIFICATION TIERS                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────┐   │
│  │     TIER 1       │  │     TIER 2       │  │    TIER 3    │   │
│  │  PostToolUse     │  │   SessionEnd     │  │   On-Demand  │   │
│  │   Light Check    │  │   Full Pipeline  │  │    Skill     │   │
│  └────────┬─────────┘  └────────┬─────────┘  └──────┬───────┘   │
│           │                     │                    │           │
│           ▼                     ▼                    ▼           │
│    Every Edit/Write      End of Session        Manual /cite     │
│    <100ms, no network    30-120s, network      2-10min, full    │
│                                                                  │
│  Checks:                 Checks:               Checks:           │
│  - DOI format            - Phase 0: CrossRef   - All 5 phases   │
│  - URL syntax            - Phase 1: HTTP       - Replacements   │
│  - Stats w/o citations   - Phase 2: Content    - Full report    │
│  - Duplicate URLs        - Phase 3: Metadata                    │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Tier 1: PostToolUse Light Check

**File:** `~/.claude/hooks/verify-citations-light.py`

**When:** After every Edit/Write operation on source files

**Checks (no network, <100ms):**
- DOI format validity (10.XXXX/suffix pattern)
- Placeholder DOI detection (10.xxxx patterns)
- URL syntax (spaces, double slashes, trailing punctuation)
- Statistics without adjacent citations (regex)
- Duplicate URLs in same edit

**Output:** Non-blocking warnings displayed in Claude Code

### Tier 2: SessionEnd Full Pipeline

**File:** `~/.claude/hooks/verify-citations-session.py`

**When:** End of each Claude Code session (automatic)

**Phases Executed:**
- Phase 0: DOI existence validation (CrossRef API)
- Phase 1: URL resolution testing (HTTP status)
- Phase 2: Content-claim alignment (heuristic matching)
- Phase 3: Metadata accuracy (author, year verification)

**Performance Limits:**
- Max 30 citations per session (configurable)
- Parallel execution with 5 workers
- 120 second timeout

**Output:** Detailed report with errors categorized by phase

### Tier 3: On-Demand Full Pipeline

**Invocation:** `/citation-verification` skill

**When:** Manual invocation for comprehensive analysis

**Features:**
- Full 5-phase pipeline with no limits
- Correction suggestions for each error
- JSON and Markdown report generation
- Integration with existing `verification_pipeline.py`

### Multi-Repository Synchronization

For projects with multiple repositories sharing the same verification infrastructure, hooks can be synchronized:

**Manual Sync:**
```bash
python scripts/sync_hooks.py
```

This copies:
1. All Python scripts in `.claude/hooks/`
2. The `hooks` section of `settings.local.json` (preserving permissions)

**Automatic Sync via Git Pre-Commit Hooks:**

Git pre-commit hooks can ensure synchronization happens automatically by detecting changes to hook files and propagating them to sibling repositories.

### Hook Configuration

**settings.local.json:**
```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Write|Edit",
        "hooks": [
          {
            "type": "command",
            "command": "python \"~/.claude/hooks/verify-citations-light.py\"",
            "timeout": 5000
          }
        ]
      }
    ],
    "SessionEnd": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "python \"~/.claude/hooks/verify-citations-session.py\"",
            "timeout": 120000
          }
        ]
      }
    ]
  }
}
```

### Error Categories in Automated Hooks

| Category | Detection Tier | Phase |
|----------|---------------|-------|
| FABRICATED_DOI | Tier 2+ | Phase 0 |
| BROKEN_URL | Tier 2+ | Phase 1 |
| CLAIM_MISMATCH | Tier 2+ | Phase 2 |
| WRONG_PAPER | Tier 2+ | Phase 2 |
| AUTHOR_ERROR | Tier 2+ | Phase 3 |
| YEAR_ERROR | Tier 2+ | Phase 3 |
| FABRICATED_STATISTIC | Tier 2+ | Phase 0+2 |
| DOI_FORMAT_ERROR | Tier 1 | Pre-Phase 0 |
| URL_SYNTAX_ERROR | Tier 1 | Pre-Phase 1 |
| MISSING_CITATION | Tier 1 | Pre-Phase 0 |

### Sample Output: Session End Report

```
============================================================
CITATION VERIFICATION (5-Phase Pipeline)
============================================================

Files checked: 3
Citations analyzed: 47
Verified correct: 38
Errors found: 7
Unable to verify: 2

--- ERRORS BY CATEGORY ---

FABRICATED DOIs (Phase 0 - not in CrossRef):
  - chapters/radiology.md:145
    https://doi.org/10.1001/fake.2024.12345

FABRICATED STATISTICS (specific numbers, no verifiable source):
  - chapters/cardiology.md:89
    Stats: 94.5%, 87.2%

CLAIM-CITATION MISMATCH (Phase 2 - content doesn't support claim):
  - chapters/history.md:234
    Confidence: 0.21

METADATA ERRORS (Phase 3 - wrong author/year):
  - chapters/oncology.md:156
    Issues: Year: cited 2023, actual 2022

============================================================
Run /citation-verification for detailed analysis and fixes.
```

### Advantages of Hook-Based Implementation

1. **Automatic:** No manual invocation required
2. **Non-blocking:** Light checks don't slow editing workflow
3. **Comprehensive:** Session-end catches all modified content
4. **Cross-repository:** Can be synchronized across multiple repositories
5. **Integrated:** Uses documented 5-phase methodology
6. **Scalable:** Parallel execution with configurable limits

---

## Conclusion

This methodology provides a systematic, reproducible approach to verifying citations in AI-generated text. The combination of automated URL testing with manual content verification ensures both link validity and claim accuracy.

### Key Findings

From verification of ~150 citations across 22 chapters:
- ~47% of citation errors were wrong papers or broken DOIs
- ~24% were metadata errors (author, year, journal)
- ~19% were claim-citation mismatches
- ~10% were metric errors

### Critical Insight: Defense in Depth

The most important learning from iterative application is that **single-layer verification is insufficient**. The Five-Layer Defense Architecture ensures:

1. **Prevention** (Layer 1): Behavioral rules prevent errors at generation time
2. **Detection** (Layer 2): Real-time hooks catch format errors immediately
3. **Gating** (Layer 3): Pre-commit validation prevents bad citations from entering codebase
4. **Deep Verification** (Layer 4): On-demand comprehensive checks for new content
5. **Efficiency** (Layer 5): Registry of verified citations avoids redundant checking

Each layer catches different error types:
- Layer 1 catches URL construction from memory (cannot be detected post-hoc)
- Layer 2 catches format errors before network calls
- Layer 3 catches citations not yet verified
- Layer 4 catches content-claim mismatches requiring human judgment
- Layer 5 reduces verification burden for known-good citations

### Generalizability

While developed for medical content, this methodology applies to any domain with academic citations:
- Legal (case law citations)
- Scientific (chemistry, physics, biology)
- Policy (government documents, regulations)
- Technical (standards documents, specifications)

The five-phase pipeline (0-4) and five-layer defense architecture are domain-agnostic. Only the claim verification in Phase 2 requires domain expertise.

---

*Document Version: 3.1*
*Last Updated: February 5, 2026*
