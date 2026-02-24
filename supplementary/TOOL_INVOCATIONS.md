# Tool Invocation Examples

**Project:** Citation Verification Pipeline
**Date:** January 18, 2026

This document contains complete, reproducible examples of every tool invocation pattern used during citation verification.

---

## Table of Contents

1. [WebFetch Invocations](#webfetch-invocations)
2. [WebSearch Invocations](#websearch-invocations)
3. [Read Tool Invocations](#read-tool-invocations)
4. [Edit Tool Invocations](#edit-tool-invocations)
5. [Grep Invocations](#grep-invocations)
6. [Parallel Agent Deployment](#parallel-agent-deployment)

---

## WebFetch Invocations

### Pattern 1: DOI Resolution Test

**Purpose:** Test if a DOI resolves to a valid paper.

**Input:**
```json
{
  "tool": "WebFetch",
  "parameters": {
    "url": "https://doi.org/10.1001/jamainternmed.2021.2626",
    "prompt": "What is the title of this paper?"
  }
}
```

**Expected Output (Success):**
```
Title: "External Validation of a Widely Implemented Proprietary Sepsis Prediction Model in Hospitalized Patients"
Authors: Wong A, Otles E, Donnelly JP, et al.
Journal: JAMA Internal Medicine
Year: 2021
```

**Expected Output (Failure - 404):**
```
Error: HTTP 404 - Not Found
The requested DOI does not resolve to any content.
```

---

### Pattern 2: Content Extraction for Claim Verification

**Purpose:** Extract specific findings from a paper to verify inline claims.

**Input:**
```json
{
  "tool": "WebFetch",
  "parameters": {
    "url": "https://doi.org/10.1001/jamainternmed.2021.2626",
    "prompt": "What sensitivity and specificity values did the Epic Sepsis Model achieve in this study? Provide exact percentages."
  }
}
```

**Expected Output:**
```
Main Findings:
- Sensitivity: 33%
- Specificity: 83%
- Positive Predictive Value (PPV): 12%
- Area Under ROC Curve (AUC): 0.63

Note: The Epic Sepsis Model showed low sensitivity (33%) meaning it missed
approximately two-thirds of sepsis cases.
```

---

### Pattern 3: Author Verification via PubMed

**Purpose:** Verify the correct author attribution for a paper.

**Input:**
```json
{
  "tool": "WebFetch",
  "parameters": {
    "url": "https://pubmed.ncbi.nlm.nih.gov/34047244/",
    "prompt": "Who are the authors of this paper? List them in order. What is the paper title?"
  }
}
```

**Expected Output:**
```
Title: "Mechanical power during extracorporeal membrane oxygenation and hospital mortality in patients with acute respiratory distress syndrome"

Authors (in order):
1. Botta M (First Author)
2. Wenstedt EFE
3. Tsonas AM
4. Buiteman-Kruizinga LA
5. et al.

Journal: Critical Care
Year: 2021
PMID: 34047244
```

---

### Pattern 4: Detecting Wrong Paper via Content Analysis

**Purpose:** Identify when a DOI points to a completely different paper than claimed.

**Input (Suspected Wrong Paper):**
```json
{
  "tool": "WebFetch",
  "parameters": {
    "url": "https://doi.org/10.1016/j.eswa.2019.02.008",
    "prompt": "What is this paper about? What is the main topic and methodology?"
  }
}
```

**Expected Output (Revealing Mismatch):**
```
Title: "A multi-agent dynamic system for robust multi-face tracking"

Topic: Computer vision - face detection and tracking
Methodology: Multi-agent system for tracking multiple faces in video
Application: Surveillance, human-computer interaction

NOTE: This paper is about FACE TRACKING, not fetal heart rate analysis.
```

**Analysis:** If the inline claim references "fetal heart rate" but the paper is about face tracking, this is a WRONG PAPER error.

---

### Pattern 5: Handling Paywalled Content

**Purpose:** Extract available metadata from paywalled sources.

**Input:**
```json
{
  "tool": "WebFetch",
  "parameters": {
    "url": "https://doi.org/10.1056/NEJMoa2212270",
    "prompt": "What is the title, authors, and publication date of this paper? What are the main conclusions visible in the abstract?"
  }
}
```

**Expected Output (Partial Access):**
```
Title: [Paper Title]
Authors: [Author List]
Journal: New England Journal of Medicine
Publication Date: 2023

Abstract Summary:
[Content from abstract if accessible]

Note: Full text requires subscription. Abstract/metadata available.
```

---

### Pattern 6: Following Redirects

**Purpose:** Handle DOI redirects to final landing page.

**Input:**
```json
{
  "tool": "WebFetch",
  "parameters": {
    "url": "https://doi.org/10.1371/journal.pone.0085071",
    "prompt": "What is this paper about? Follow any redirects."
  }
}
```

**Expected Redirect Chain:**
```
1. https://doi.org/10.1371/journal.pone.0085071
   → 302 Redirect
2. https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0085071
   → 200 OK
   → Final content retrieved
```

---

## WebSearch Invocations

### Pattern 1: Finding Correct DOI for Known Paper

**Purpose:** Locate the correct DOI when the cited DOI is broken.

**Input:**
```json
{
  "tool": "WebSearch",
  "parameters": {
    "query": "Slight drug safety surveillance adverse events detection 2013 PLOS DOI"
  }
}
```

**Expected Output:**
```
Search Results:

1. "Using Routinely Collected Data to Identify Patients at Risk
   for Medication-Related Problems"
   - Authors: Slight SP, Seger DL, Nanji KC, et al.
   - Journal: PLOS ONE
   - Year: 2013
   - DOI: 10.1371/journal.pone.0085071
   - URL: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0085071

2. [Additional results...]
```

---

### Pattern 2: Verifying Paper Existence

**Purpose:** Confirm that a cited paper actually exists.

**Input:**
```json
{
  "tool": "WebSearch",
  "parameters": {
    "query": "Green University Michigan deterioration index cardiac arrest 2019 JAMA"
  }
}
```

**Expected Output (Paper Does Not Exist):**
```
Search Results:

No results found for "Green et al." + "University of Michigan" +
"deterioration index" + "cardiac arrest" + "2019" + "JAMA"

Related results found:
1. Michigan Medicine deployed early warning systems but no
   peer-reviewed publication by "Green et al." found
2. General articles about deterioration indices at Michigan

CONCLUSION: No peer-reviewed paper matching this citation exists.
```

---

### Pattern 3: Finding Paper Matching Specific Claim

**Purpose:** Find a legitimate paper that supports a specific claim.

**Input:**
```json
{
  "tool": "WebSearch",
  "parameters": {
    "query": "fetal heart rate CTG cardiotocography deep learning classification 2019 2020 DOI accuracy"
  }
}
```

**Expected Output:**
```
Search Results:

1. "DeepFHR: Deep learning approach for automatic fetal heart rate
   classification from cardiotocography"
   - Authors: Zhao Z, Zhang Y, Deng Y
   - Journal: BMC Medical Informatics and Decision Making
   - Year: 2019
   - DOI: 10.1186/s12911-019-0891-1
   - Finding: Achieved 98.34% accuracy in fetal heart rate classification

2. [Additional results...]
```

---

### Pattern 4: Cross-Reference Verification

**Purpose:** Verify metadata across multiple sources.

**Input:**
```json
{
  "tool": "WebSearch",
  "parameters": {
    "query": "Tschandl skin lesion classification Lancet Oncology 2019 publication date"
  }
}
```

**Expected Output:**
```
Search Results:

1. "Comparison of the accuracy of human readers versus machine-learning
   algorithms for pigmented skin lesion classification"
   - First Author: Tschandl P
   - Journal: Lancet Oncology
   - Publication Date: July 2019 (Volume 20, Issue 7)
   - DOI: 10.1016/S1470-2045(19)30333-X

   Note: DOI suffix "19" confirms 2019 publication year
```

---

### Pattern 5: Finding Alternative When Primary Source Unavailable

**Purpose:** Find systematic reviews or meta-analyses when primary source is problematic.

**Input:**
```json
{
  "tool": "WebSearch",
  "parameters": {
    "query": "antimicrobial stewardship clinical decision support systematic review meta-analysis effectiveness"
  }
}
```

**Expected Output:**
```
Search Results:

1. "Impact of Rapid Diagnostics with Antimicrobial Stewardship Support:
   A Systematic Review and Meta-analysis"
   - Authors: Timbrook TT, et al.
   - Journal: Clinical Infectious Diseases
   - Year: 2017
   - DOI: 10.1093/cid/ciw837

2. "Clinical decision support systems for antimicrobial prescribing"
   - Cochrane Review
   - [Details...]
```

---

## Read Tool Invocations

### Pattern 1: Initial File Content Extraction

**Purpose:** Read a chapter file to identify all citations.

**Input:**
```json
{
  "tool": "Read",
  "parameters": {
    "file_path": "specialties/infectious-diseases.qmd"
  }
}
```

**Output:** Full file content with line numbers for precise editing.

---

### Pattern 2: Targeted Section Reading

**Purpose:** Read specific lines around a citation for context.

**Input:**
```json
{
  "tool": "Read",
  "parameters": {
    "file_path": "specialties/critical-care.qmd",
    "offset": 150,
    "limit": 50
  }
}
```

**Output:** Lines 150-200 containing the citation and surrounding context.

---

### Pattern 3: Extracting Inline Claims

**Purpose:** Extract the exact claim made before/after a citation.

**Process:**
1. Read file
2. Locate citation URL
3. Extract 200 characters before and after
4. Parse for statistics, findings, conclusions

**Example Context Extraction:**
```
Before citation:
"The Epic Sepsis Model showed 33% sensitivity and 67% specificity"

Citation:
([Wong et al., 2021](https://doi.org/10.1001/jamainternmed.2021.2626))

After citation:
"in the external validation study at Michigan Medicine"
```

---

## Edit Tool Invocations

### Pattern 1: Fixing Broken DOI

**Purpose:** Replace a broken DOI with the correct one.

**Input:**
```json
{
  "tool": "Edit",
  "parameters": {
    "file_path": "specialties/infectious-diseases.qmd",
    "old_string": "([Slight et al., 2013](https://doi.org/10.1007/s40264-013-0089-1))",
    "new_string": "([Slight et al., 2013](https://doi.org/10.1371/journal.pone.0085071))"
  }
}
```

---

### Pattern 2: Correcting Author Attribution

**Purpose:** Fix wrong first author name.

**Input:**
```json
{
  "tool": "Edit",
  "parameters": {
    "file_path": "specialties/critical-care.qmd",
    "old_string": "([Arnal et al., 2021](https://pubmed.ncbi.nlm.nih.gov/34047244/))",
    "new_string": "([Botta et al., 2021](https://doi.org/10.1186/s13054-021-03611-y))"
  }
}
```

---

### Pattern 3: Fixing Metric Error in Text

**Purpose:** Correct a wrong statistic in the inline text.

**Input:**
```json
{
  "tool": "Edit",
  "parameters": {
    "file_path": "specialties/infectious-diseases.qmd",
    "old_string": "67% specificity",
    "new_string": "83% specificity"
  }
}
```

---

### Pattern 4: Removing Fabricated Citation

**Purpose:** Remove an unverifiable claim and citation entirely.

**Input:**
```json
{
  "tool": "Edit",
  "parameters": {
    "file_path": "specialties/critical-care.qmd",
    "old_string": "One study at the University of Michigan reported a 35% reduction in cardiac arrests outside the ICU after implementing their deterioration index ([Green et al., 2019](https://doi.org/10.1001/jamanetworkopen.2019.14004)).",
    "new_string": "Hospital implementations of early warning systems have reported improvements in identifying deteriorating patients, though peer-reviewed validation varies."
  }
}
```

---

### Pattern 5: Fixing Year Error

**Purpose:** Correct wrong publication year.

**Input:**
```json
{
  "tool": "Edit",
  "parameters": {
    "file_path": "specialties/dermatology.qmd",
    "old_string": "[Tschandl et al., 2020]",
    "new_string": "[Tschandl et al., 2019]"
  }
}
```

---

### Pattern 6: Replacing Wrong Paper with Correct One

**Purpose:** Replace a citation that points to wrong paper with correct paper.

**Input:**
```json
{
  "tool": "Edit",
  "parameters": {
    "file_path": "specialties/obgyn.qmd",
    "old_string": "([Zhao et al., 2019](https://doi.org/10.1016/j.eswa.2019.02.008))",
    "new_string": "([Zhao et al., 2019](https://doi.org/10.1186/s12911-019-0891-1))"
  }
}
```

---

### Pattern 7: Rephrasing Claim to Match Citation

**Purpose:** When citation is correct but claim overstates findings.

**Input:**
```json
{
  "tool": "Edit",
  "parameters": {
    "file_path": "foundations/ai-basics.qmd",
    "old_string": "Clinicians presented with AI-generated diagnoses accepted incorrect AI suggestions more readily than incorrect suggestions attributed to human consultants",
    "new_string": "Systematic review found automation bias increased risk of commission errors by 26% when using incorrect decision support"
  }
}
```

---

## Grep Invocations

### Pattern 1: Finding All Instances of a Citation

**Purpose:** Locate all occurrences of a specific citation across all files.

**Input:**
```json
{
  "tool": "Grep",
  "parameters": {
    "pattern": "Wong et al., 2021",
    "path": ".",
    "glob": "*.qmd",
    "output_mode": "content"
  }
}
```

**Expected Output:**
```
specialties/critical-care.qmd:145: ([Wong et al., 2021](https://doi.org/10.1001/jamainternmed.2021.2626))
foundations/history.qmd:256: ([Wong et al., 2021](https://doi.org/10.1001/jamainternmed.2021.2626))
```

---

### Pattern 2: Finding All DOI Citations

**Purpose:** Extract all DOI-based citations for batch processing.

**Input:**
```json
{
  "tool": "Grep",
  "parameters": {
    "pattern": "doi\\.org/10\\.[0-9]+",
    "path": "specialties/",
    "glob": "*.qmd",
    "output_mode": "content"
  }
}
```

---

### Pattern 3: Finding Broken URL Patterns

**Purpose:** Identify citations with known broken URL patterns.

**Input:**
```json
{
  "tool": "Grep",
  "parameters": {
    "pattern": "doi.org/10.1007/s40264-013-0089",
    "path": ".",
    "glob": "*.qmd",
    "output_mode": "files_with_matches"
  }
}
```

---

### Pattern 4: Verifying Correction Applied Across All Files

**Purpose:** Confirm a correction was applied everywhere.

**Input (After Correction):**
```json
{
  "tool": "Grep",
  "parameters": {
    "pattern": "Arnal et al",
    "path": ".",
    "glob": "*.qmd",
    "output_mode": "count"
  }
}
```

**Expected Output (After Correction):**
```
Total matches: 0
```

(Confirming all "Arnal et al" instances have been corrected to "Botta et al")

---

## Parallel Agent Deployment

### Pattern 1: Batch Verification Across Chapters

**Purpose:** Verify multiple chapters simultaneously for efficiency.

**Deployment Configuration:**
```
Task Tool invocations (deployed in parallel):

Agent 1:
{
  "tool": "Task",
  "parameters": {
    "description": "Verify obgyn citations",
    "prompt": "Read specialties/obgyn.qmd. For EACH citation URL, use WebFetch to verify the URL resolves and the paper content matches the inline claim. Report all errors found.",
    "subagent_type": "general-purpose"
  }
}

Agent 2:
{
  "tool": "Task",
  "parameters": {
    "description": "Verify critical-care citations",
    "prompt": "Read specialties/critical-care.qmd. For EACH citation URL, use WebFetch to verify the URL resolves and the paper content matches the inline claim. Report all errors found.",
    "subagent_type": "general-purpose"
  }
}

Agent 3:
{
  "tool": "Task",
  "parameters": {
    "description": "Verify oncology citations",
    "prompt": "Read specialties/oncology.qmd. For EACH citation URL, use WebFetch to verify the URL resolves and the paper content matches the inline claim. Report all errors found.",
    "subagent_type": "general-purpose"
  }
}

[Continue for all chapters...]
```

---

### Pattern 2: Parallel Correction Application

**Purpose:** Apply corrections to multiple chapters simultaneously.

**Deployment Configuration:**
```
Task Tool invocations (deployed in parallel):

Agent 1:
{
  "tool": "Task",
  "parameters": {
    "description": "Fix neurology citations",
    "prompt": "Apply the following corrections to specialties/neurology.qmd:
    1. Change [Citation A] to [Corrected A]
    2. Change [Citation B] to [Corrected B]
    Use the Edit tool for each correction. Verify each edit was applied correctly.",
    "subagent_type": "general-purpose"
  }
}

Agent 2:
{
  "tool": "Task",
  "parameters": {
    "description": "Fix psychiatry citations",
    "prompt": "Apply the following corrections to specialties/psychiatry.qmd:
    [Corrections list...]",
    "subagent_type": "general-purpose"
  }
}

[Continue for all chapters needing corrections...]
```

---

### Pattern 3: Verification Report Generation

**Purpose:** Generate verification reports for each section.

**Agent Prompt Template:**
```
Read all .qmd files in [directory].
For each file:
1. Extract all markdown citations matching pattern [Author, Year](URL)
2. Test each URL with WebFetch
3. Compare inline claims to paper content
4. Document any discrepancies

Generate a report in this format:
- File: [filename]
- Total citations: [count]
- Verified correct: [count]
- Errors found: [list with details]
```

---

## Verification Checklist

For each citation, execute this verification sequence:

```
□ Step 1: WebFetch URL
  └─ Status 200? → Proceed
  └─ Status 404? → Flag BROKEN
  └─ Status 302? → Follow redirect, verify final content

□ Step 2: Extract paper metadata
  └─ Title matches expected topic?
  └─ Authors match citation?
  └─ Year matches citation?

□ Step 3: Compare claim to content
  └─ Statistics match?
  └─ Findings support claim?
  └─ No semantic mismatch?

□ Step 4: Apply correction if needed
  └─ Edit tool with old_string/new_string
  └─ Verify edit applied correctly

□ Step 5: Cross-file verification
  └─ Grep for same citation in other files
  └─ Apply same correction if found
```

---

*Document Version: 1.0*
*Last Updated: January 18, 2026*
