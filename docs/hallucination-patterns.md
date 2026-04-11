# Citation Hallucination Patterns

This document describes hallucination patterns in AI-generated academic content. These patterns are organized into three tiers based on detection difficulty and the verification phase required to catch them.

## Overview

Citation hallucinations range from structural failures (broken URLs, fabricated DOIs) to semantic misrepresentation (valid papers that do not support the specific claim). Standard URL verification catches approximately 21% of errors. The remaining 79% require content-level verification.

### Tier 1: Structural Failures (Phases 0-1)

Detectable through automated HTTP and API checks.

| Pattern | Severity | Detection | Frequency |
|---------|----------|-----------|-----------|
| Non-Existent DOI | High | Easy | Common |
| Memory-Constructed URL | Critical | Easy (post-hoc) | Common |
| Wrong Publisher Prefix | Medium | Easy | Occasional |

### Tier 2: Content-Level Failures (Phase 2)

Require reading the paper and comparing against the specific claim.

| Pattern | Severity | Detection | Frequency |
|---------|----------|-----------|-----------|
| Valid DOI, Wrong Paper | Critical | Medium | Common |
| Wrong Metadata | Medium | Medium | Very Common |
| Completely Fabricated | Critical | Easy-Medium | Occasional |
| Chimera Citation | Critical | Hard | Occasional |
| Misattributed Authorship | Medium | Medium | Common |
| Truncated/Corrupted Metadata | Low-Medium | Easy | Very Common |
| Edition/Version Confusion | Medium | Hard | Occasional |
| Citation Overloading | High | Medium | Occasional |
| Reverse Overloading | High | Hard | Occasional |
| Statistical Conflation | High | Hard | Occasional |
| Table/Figure Misread | Critical | Hard | Occasional |
| Secondary Source Attribution | Medium | Hard | Occasional |
| Self-Referential Loop | Critical | Medium | Rare (RAG) |
| Withdrawn/Corrected Paper | High | Medium | Occasional |

### Tier 3: Semantic Failures (Phase 2+)

Require domain expertise to detect. The citation is structurally valid, the paper is real and on-topic, but the relationship between claim and source is misrepresented.

| Pattern | Severity | Detection | Frequency |
|---------|----------|-----------|-----------|
| Scope Extrapolation | High | Hard | Common |
| Evidence Strength Inflation | High | Hard | Very Common |
| Causal Inference Escalation | High | Hard | Common |
| Direction-of-Effect Reversal | Critical | Hard | Occasional |
| Retracted Paper Citation | Critical | Medium | Occasional |
| Superseded Evidence | Medium | Medium | Common |
| Drug Name Substitution | Critical | Hard | Rare (medical) |
| Geographic Mismatch | Medium | Hard | Common |
| Conference Abstract as Paper | Medium | Medium | Occasional |
| Preprint-as-Published | Medium | Medium | Common |
| Dosage/Unit Transposition | Critical | Hard | Rare (medical) |
| Confidence Interval Fabrication | High | Hard | Occasional |
| Ghost Update | High | Hard | Occasional |
| Off-Label Indication Conflation | Critical | Hard | Rare (medical) |
| Survival Bias in Source Selection | High | Hard | Common |
| Regulatory Status Mismatch | High | Hard | Occasional |

## Pattern 1: Valid DOI, Wrong Paper

**What it looks like**: The DOI is syntactically correct and resolves to a real paper, but it's a completely different paper than claimed.

**Example**:
```
Citation claims: Smith et al., 2021, "Deep learning for cancer detection"
DOI provided: 10.1038/s41591-019-0649-9
DOI actually resolves to: Jones et al., 2019, "Machine learning skin classification"
```

**Why it happens**:
- AI generates plausible DOI patterns but gets the suffix wrong
- Copy-paste errors mixing citations
- DOIs from related papers in the same journal

**Detection method**:
1. Resolve the DOI via CrossRef API
2. Compare the actual title/authors against the claimed citation
3. Flag significant mismatches

**How to fix**:
1. Search for the actual paper using the claimed title and authors
2. Find the correct DOI from the publisher or PubMed
3. Replace the incorrect DOI

**Risk level**: CRITICAL. The paper exists, so basic validation passes, but the content being cited is completely different.

---

## Pattern 2: Non-Existent DOI (404)

**What it looks like**: The DOI follows valid syntax but doesn't exist in the DOI system.

**Example**:
```
Citation: Johnson et al., 2020, Journal of Medical AI
DOI: 10.1016/j.jmai.2020.100234
Result: HTTP 404 - DOI not found
```

**Why it happens**:
- AI generates DOIs following observed patterns
- Typos in manual entry (one digit off)
- DOIs from preprints that never got final DOIs
- Papers that were retracted and DOI deleted

**Detection method**:
1. Send HTTP HEAD request to `https://doi.org/{DOI}`
2. Check for 404 or redirect failure
3. Any non-200 response indicates problem

**How to fix**:
1. Search for the paper by title/author in Google Scholar or PubMed
2. If found, use the correct DOI
3. If not found, the paper may not exist (Pattern 4)

**Risk level**: HIGH. Easy to detect but indicates the citation may be entirely fabricated.

---

## Pattern 3: Wrong Year or Author Metadata

**What it looks like**: The DOI is correct, but the citation text has wrong author names or publication year.

**Example**:
```
Citation text: "Williams et al., 2022"
DOI: 10.1056/NEJMoa2035389
Actual paper: Williams et al., 2021 (published December 2020, assigned 2021)
```

**Why it happens**:
- Confusion between online publication date and print date
- Papers with large author lists and variant name spellings
- AI confusing similar papers by same research group
- Multi-year research projects with multiple related papers

**Detection method**:
1. Fetch metadata from CrossRef
2. Compare publication year (allow some flexibility for Dec/Jan edge cases)
3. Check if any author's last name matches the citation

**How to fix**:
1. Use the year from the DOI metadata
2. Match author names to the actual paper
3. Update citation text to match reality

**Risk level**: MEDIUM. Paper is correctly referenced but citation text is misleading.

---

## Pattern 4: Completely Fabricated Citation

**What it looks like**: The paper, authors, and journal don't exist. The DOI either doesn't resolve or points to an unrelated paper.

**Example**:
```
Citation: "Chen et al., 2023, Nature AI Medicine"
DOI: 10.1038/s41591-2023-04521-x
Problem: "Nature AI Medicine" is not a real journal
         DOI returns 404
         No paper by these authors on this topic exists
```

**Why it happens**:
- AI hallucination generating plausible-sounding citations
- Fabricated to support claims that lack real evidence
- Mixing real journal names with fake suffixes

**Detection method**:
1. DOI resolution fails (404)
2. Journal name not in known journals list
3. Author + title search returns no results
4. Multiple verification methods fail together

**How to fix**:
1. Search for real papers on the topic
2. Replace with legitimate citations that support the claim
3. If no supporting evidence exists, remove the claim

**Risk level**: CRITICAL. Citing non-existent research is a serious integrity issue.

---

## Pattern 5: Wrong Publisher Prefix

**What it looks like**: The DOI prefix doesn't match the claimed journal's publisher.

**Example**:
```
Citation claims: Nature Medicine
DOI: 10.1001/jamanetworkopen.2023.1234
Problem: 10.1001 is JAMA Network, not Nature (10.1038)
```

**Common publisher prefixes**:
| Prefix | Publisher |
|--------|-----------|
| 10.1038 | Nature/Springer Nature |
| 10.1001 | JAMA Network (AMA) |
| 10.1056 | New England Journal of Medicine |
| 10.1016 | Elsevier |
| 10.1136 | BMJ |
| 10.1093 | Oxford University Press |
| 10.1371 | PLOS |
| 10.1126 | Science (AAAS) |
| 10.1161 | AHA Journals (Circulation, etc.) |
| 10.1002 | Wiley |

**Why it happens**:
- AI generates DOI with wrong prefix
- Copy-paste from wrong source
- Confusion between journals with similar names

**Detection method**:
1. Extract DOI prefix (before the slash)
2. Look up expected prefix for claimed journal
3. Flag mismatches

**How to fix**:
1. Find the paper in the correct journal
2. Use the proper DOI with matching prefix
3. Or correct the journal name to match the DOI's publisher

**Risk level**: MEDIUM. Usually indicates simple confusion, but could mask Pattern 1 or 4.

---

## Pattern 6: Memory-Constructed URLs (Non-DOI Links)

**What it looks like**: URLs for non-DOI links (government sites, news articles, organizational pages) are constructed from memory based on URL patterns, not extracted from search results.

**Example**:
```
LLM constructs: https://www.whitehouse.gov/ostp/news-updates/2023/07/21/new-pandemic-office/
Actual location: https://bidenwhitehouse.archives.gov/briefing-room/statements-releases/2023/07/21/fact-sheet-white-house-launches-office-of-pandemic-preparedness-and-response-policy/
```

**Why it happens**:
- AI remembers URL patterns from training data (e.g., "White House announcements are at whitehouse.gov/ostp/...")
- AI doesn't know when content has been archived, restructured, or moved
- Government transitions cause mass URL migrations (administration changes)
- Organizations redesign sites, breaking all old paths

**Detection method**:
1. Cannot be detected by automated syntax checks (URL looks valid)
2. Only caught by post-hoc HTTP verification (404 error)
3. By then, the error is already in the content

**How to fix**:
1. **Prevention is the only solution**: Never construct URLs from memory
2. Always WebSearch for the content and extract the exact URL from search results
3. If URL verification fails, search for the new location

**Risk level**: CRITICAL for dynamic content. Government sites, news articles, and organizational pages change URLs frequently. DOIs are stable; web URLs are not.

**Key distinction from Pattern 2 (Non-Existent DOI)**:
- Pattern 2: DOI format is correct but DOI doesn't exist
- Pattern 6: URL format is correct but the page doesn't exist at that path (often because it moved)

**Enforcement**: Pre-generation behavioral rule, not post-hoc verification. The rule: "Only use URLs extracted from current WebSearch results or provided by the user."

---

## Pattern 7: Misattributed Authorship

**What it looks like**: The citation uses a city, publisher, or organization name where individual author names should appear, or vice versa.

**Example**:
```
Citation text: "Geneva: World Health Organization, 2021"
Problem: "Geneva" is treated as the author in the in-text citation
Correct: WHO is the corporate author; "Geneva" is the place of publication
```

Another variant:
```
Citation text: "WHO, 2021"
Problem: No individual authors listed despite the document having named authors
Correct: "Smith J, Jones A, et al. [Title]. Geneva: World Health Organization; 2021"
```

**Why it happens**:
- Confusion between publisher location and authorship field in reference managers
- Corporate authorship conventions vary by citation style (APA, Vancouver, AMA)
- AI models confuse bibliographic fields (city, publisher, author) when generating citations
- Some organizational reports genuinely use corporate authorship; others have named individual authors

**Detection method**:
1. Check if the "author" field contains a city name (Geneva, Washington, London)
2. Look up the actual document to determine if individual authors are listed
3. Verify corporate vs. individual authorship against the title page

**How to fix**:
1. Check the source document's title page for named authors
2. If individual authors exist, cite them (with corporate author as publisher)
3. If corporate authorship is correct, remove the city from the author field

**Risk level**: MEDIUM. The paper exists and is correctly identified, but misattribution can make the reference list look careless and complicates lookup by other researchers.

---

## Pattern 8: Truncated or Corrupted Metadata

**What it looks like**: Journal names, titles, or other metadata fields are cut short, misspelled, or garbled.

**Example**:
```
Citation text: "Lancet Digit"
Correct: "The Lancet Digital Health"

Citation text: "J Med Internet"
Correct: "Journal of Medical Internet Research"
```

**Why it happens**:
- Reference manager export errors (field length limits)
- Copy-paste from databases that abbreviate journal names
- AI generating partial journal names from training data patterns
- Character encoding issues corrupting special characters in titles
- Manual transcription cutting off long journal names

**Detection method**:
1. Compare journal names against the NLM Catalog or ISSN database
2. Check for unusually short journal name strings (under 15 characters for multi-word journals)
3. Look for missing articles ("Lancet" vs. "The Lancet"), missing subtitles, or trailing fragments

**How to fix**:
1. Look up the full journal name in PubMed/NLM Catalog
2. Use the standard abbreviation (NLM style) or full name consistently
3. Verify all metadata fields (volume, issue, pages) are complete

**Risk level**: LOW-MEDIUM. The reference is identifiable but looks unprofessional. In automated verification pipelines, truncated names can cause false negatives (journal name doesn't match known databases).

---

## Pattern 9: Preprint Cited as Published

**What it looks like**: A preprint (arXiv, bioRxiv, medRxiv, SSRN) is cited as if it were a peer-reviewed published article, without any indication of its preprint status.

**Example**:
```
Citation text: "Zhang et al., Nature Medicine, 2023"
Actual status: Posted on medRxiv, never published in Nature Medicine
```

Or:
```
Citation text: "Park et al., 2024. Journal of Clinical Investigation"
Actual status: Published in JCI, but was a medRxiv preprint when the citing manuscript was drafted.
The preprint version had different conclusions than the published version.
```

**Why it happens**:
- Authors cite preprints found during literature search without checking publication status
- AI models don't distinguish between preprint and published versions in training data
- Preprints sometimes have different findings than the final published version
- Some preprints are never published (peer review identified fatal flaws)
- Rapid-moving fields (COVID-19) have many preprints that were never peer-reviewed

**Detection method**:
1. Search for the paper title in PubMed (which indexes published articles, not preprints)
2. If only found on preprint servers, it has not been peer-reviewed
3. If found in both, compare the preprint and published versions for substantive differences
4. Check the DOI prefix: 10.1101 (bioRxiv/medRxiv), 10.48550 (arXiv) indicate preprints

**How to fix**:
1. If a published version exists, update the citation to the published version
2. If only a preprint exists, label it explicitly: "Author et al., 2023, preprint"
3. Note if findings changed between preprint and publication
4. Consider whether a preprint (unreviewed) is appropriate evidence for the claim being made

**Risk level**: MEDIUM. Citing preprints as published inflates the apparent strength of evidence. In clinical contexts, this can be dangerous: a preprint with promising results might be cited to support a clinical recommendation, but the peer-reviewed version may have revealed methodological problems.

---

## Pattern 10: Edition or Version Confusion

**What it looks like**: A guideline, framework, or living document is cited by the wrong edition, version, or year of publication, often confusing an older version with a more recent update.

**Example**:
```
Citation text: "CONSORT Statement (Moher et al., 2001)"
Problem: CONSORT 2010 is the current version (Schulz et al., 2010)
The 2001 version is obsolete
```

Another variant:
```
Citation text: "PRISMA guidelines (Moher et al., 2009)"
Problem: PRISMA 2020 is the current version (Page et al., 2021)
Citing the 2009 version suggests the authors are unaware of the update
```

**Why it happens**:
- AI training data includes citations to older versions that were more commonly cited historically
- Authors copy citations from older papers without checking for updates
- Some frameworks change lead authors between versions (CONSORT: Moher → Schulz; PRISMA: Moher → Page)
- Living documents may have multiple versions without clear deprecation notices

**Detection method**:
1. Check the cited framework's official website for the current version
2. Compare the year and lead author against the most recent edition
3. Verify the DOI resolves to the version actually cited (not redirected to an update)

**How to fix**:
1. Identify the current version of the guideline or framework
2. Update citation to reflect current edition with correct authors and year
3. If citing the older version intentionally (e.g., historical comparison), state this explicitly

**Risk level**: MEDIUM. Citing outdated guidelines suggests the authors are not current with the field. In regulatory or clinical contexts, applying an obsolete standard could have practical consequences.

---

## Combined Pattern Detection

The most reliable verification uses multiple checks together:

```
Citation: "Author et al., Year, Journal Title"
DOI: 10.xxxx/suffix

Check 1: Does DOI resolve? (Pattern 2)
Check 2: Does prefix match journal? (Pattern 5)
Check 3: Do authors/year match metadata? (Pattern 3)
Check 4: Does title match claimed topic? (Pattern 1)
Check 5: Does journal name exist? (Pattern 4)
Check 6: Is the "author" actually an author, not a city or publisher? (Pattern 7)
Check 7: Is the journal name complete and correctly spelled? (Pattern 8)
Check 8: Is this the published version, or a preprint? (Pattern 9)
Check 9: Is this the current edition/version? (Pattern 10)
```

If multiple checks fail, the citation is likely Pattern 4 (completely fabricated).

## Why AI Generates These Errors

Large language models generate citations by:

1. **Pattern completion**: Generating DOI-like strings that follow observed patterns
2. **Semantic plausibility**: Creating author names and titles that sound reasonable
3. **Statistical likelihood**: Combining common elements (journal names, years, topics)

The model doesn't have access to the actual DOI database, so it can't verify that generated DOIs exist or point to the claimed papers.

---

## Pattern 7: Scope Extrapolation

**What it looks like**: A study on 50 patients at one hospital is cited as evidence for a population-level claim. The paper is real, the numbers are correct, but the generalizability claim is fabricated by the LLM.

**Example**:
```
Claim: "AI-assisted diagnosis has been widely shown to improve outcomes"
Paper: Single-center pilot study, n=47, one hospital, preliminary results
```

**Why it happens**:
- LLMs do not distinguish study scope from claim scope
- Training data conflates pilot results with established evidence
- Broad language ("widely," "generally") is statistically common in training text

**Detection method**:
1. Extract study population and setting from paper content
2. Compare against scope language in inline claim
3. Flag when claim scope exceeds study scope (single-site cited as population-level)

**How to fix**:
1. Add scope qualifiers: "In a single-center pilot study of 47 patients..."
2. Or find a systematic review that supports the broader claim

---

## Pattern 8: Evidence Strength Inflation

**What it looks like**: Preliminary evidence cited as established. A case report becomes "studies show," a pilot study becomes "research demonstrates," a preprint becomes "peer-reviewed evidence confirms."

**Example**:
```
Claim: "Research has demonstrated that this approach reduces mortality by 30%"
Paper: Case series of 12 patients, no control group, conference abstract
```

**Why it happens**:
- LLMs generate confident-sounding language by default
- Training incentives reward assertive claims over hedged statements
- "Demonstrated" scores higher than "A small case series suggested" in training

**Detection method**:
1. Classify study design (RCT > cohort > case-control > case series > case report)
2. Identify claim strength language ("demonstrated" vs. "suggested")
3. Flag when claim strength exceeds study design level

---

## Pattern 9: Causal Inference Escalation

**What it looks like**: An observational study is cited as causal evidence. "X is associated with Y" in the paper becomes "X causes Y" in the LLM output. 64-72% of residual hallucinations stem from causal/temporal reasoning failures.

**Example**:
```
Claim: "Telehealth reduces hospital readmissions"
Paper: Cross-sectional survey showing association between telehealth access and lower readmission rates (no causal design)
```

**Detection method**:
1. Identify causal language ("causes," "leads to," "reduces," "prevents")
2. Classify cited study design
3. Flag causal language when study design is observational

---

## Pattern 10: Retracted Paper Citation

**What it looks like**: LLM cites a paper that has been formally retracted. The DOI resolves, the paper appears real, but the findings have been invalidated.

**Detection method**:
1. After DOI validation, query CrossRef `update-to` field
2. Check `relation.is-retracted-by` field
3. Cross-reference Retraction Watch database

---

## Pattern 11: Direction-of-Effect Reversal

**What it looks like**: The paper and topic are correct, but the qualitative finding is inverted. A paper showing "93% concordance" (positive) gets cited as showing "significant disparities" (negative). The topic matches; only the directional framing is wrong.

**Why it happens**:
- Questions containing directional terms ("more," "less") steer LLM predictions
- LLMs generate text that matches the surrounding narrative direction
- Direction-of-effect is a subtle property that requires reading the paper

**Detection method**:
1. Extract directional framing from claim (positive/negative/neutral)
2. Compare against paper's actual conclusion direction
3. Flag when directions conflict

---

## Pattern 12: Citation Overloading

**What it looks like**: A single citation is attached to a sentence that actually synthesizes claims from multiple distinct papers. The cited paper supports one element of the claim; the rest is unattributed or fabricated.

**Example**:
```
Claim: "AI systems have shown 94% accuracy in chest X-ray reading, reduced radiologist
        fatigue by 40%, and cut reporting time by 25% [Smith et al., 2022]"
Smith et al., 2022: Only reports the 94% accuracy figure. The fatigue and time data
                   come from different unpublished or fabricated sources.
```

**Why it happens**:
- LLMs batch multiple facts under a single familiar citation
- The cited paper is real and partially relevant, reducing detection probability
- Training data includes writing where compound claims share one citation

**Detection method**:
1. Decompose compound claims into atomic sub-claims
2. Verify each sub-claim independently against the cited paper
3. Flag when paper supports only a subset of the attributed claims

**How to fix**:
1. Find separate citations for each sub-claim
2. Or restructure into separate sentences with separate citations
3. Remove sub-claims that cannot be independently sourced

**Risk level**: HIGH. Passes Phase 0-1 completely. Only Phase 2 with atomic claim decomposition detects this.

---

## Pattern 13: Reverse Overloading

**What it looks like**: Multiple real citations are provided for a single claim, but the claim is a synthesis that no individual paper actually makes. Each citation supports a component, but the assembled conclusion is the LLM's own inference.

**Example**:
```
Claim: "AI diagnostic tools reduce costs by 35% while maintaining safety" [A, B, C]
Paper A: Reports 35% cost reduction (different context)
Paper B: Reports maintained safety (different intervention)
Paper C: Reviews AI diagnostics generally
No paper makes the combined cost-plus-safety claim.
```

**Why it happens**:
- LLMs synthesize across papers as a core capability
- The synthesis feels like a conclusion the evidence supports
- Multiple citations create an appearance of thorough sourcing

**Detection method**:
1. For multi-citation claims, verify the assembled claim appears in at least one source
2. Flag when all supporting papers address components but none address the combination

**Risk level**: HIGH. Particularly dangerous in systematic review contexts where synthesis is expected.

---

## Pattern 14: Statistical Conflation

**What it looks like**: Figures from different study populations, time periods, or measurement contexts are merged into one number attributed to a single source.

**Example**:
```
Claim: "Diagnostic AI achieves 87-93% accuracy across imaging modalities [Lee et al., 2021]"
Lee et al., 2021: Reports 87% for CT only.
The 93% figure comes from a different paper on MRI, or is fabricated.
The range implies Lee covers both; it does not.
```

**Why it happens**:
- LLMs generate ranges to appear precise and comprehensive
- Training data includes ranges assembled from multiple sources without attribution
- Both numbers may individually exist in the literature; the attribution is wrong

**Detection method**:
1. For range claims (X-Y%), verify both endpoints appear in the same cited source
2. Check that both endpoints describe the same population and measurement
3. Flag when range endpoints cannot both be located in the cited paper

**Risk level**: HIGH. Ranges signal comprehensive evidence but can mask selective or fabricated attribution.

---

## Pattern 15: Preprint-as-Published

**What it looks like**: A preprint is cited as though it is peer-reviewed and published, or a preprint citation is used when the paper has since been published with materially different conclusions.

**Example**:
```
Citation: "[Author et al., 2023](https://doi.org/10.1101/2023.04.15.537048)"
Problem 1: bioRxiv preprint presented without "preprint" qualifier
Problem 2: Published version (2024) reports lower effect size after peer review revision
```

**Why it happens**:
- LLMs cannot distinguish preprint from published status
- bioRxiv/medRxiv DOIs look identical in format to published DOIs
- Preprint servers have grown substantially; training data includes many unqualified preprint citations

**Detection method**:
1. Check DOI prefix: `10.1101/` = bioRxiv/medRxiv preprint
2. Check CrossRef `type` field for "posted-content"
3. Search for published version; compare conclusions if found

**How to fix**:
1. Add "preprint" qualifier to citation text
2. If published version exists with different conclusions, cite the published version and note revisions
3. Downgrade claim confidence to match preprint status

**Risk level**: MEDIUM. Preprint findings are not peer-reviewed and can change significantly before publication.

---

## Pattern 16: Dosage/Unit Transposition

**What it looks like**: The drug name and paper are correct, but specific dosages, units, frequencies, or administration routes are wrong. Distinct from Drug Name Substitution (Pattern already documented), where the wrong drug is cited.

**Example**:
```
Claim: "Standard dosing is 5 mg/kg daily [Chen et al., 2022]"
Chen et al., 2022: Actually reports 5 mg/kg twice daily (BID)
                   or reports 0.5 mg/kg (tenfold error)
                   or reports 5 mcg/kg (mg vs mcg unit swap)
```

**Why it happens**:
- LLMs generate plausible-sounding doses from distributional knowledge of the drug class
- mg/mcg and daily/BID transpositions are common in training data
- Dose is a minor detail; LLMs prioritize the drug-indication match

**Detection method**:
1. For any dosing claim, extract exact dose, unit, frequency, and route from cited paper
2. Compare all four elements against the inline claim
3. Any discrepancy in any element is a critical error in medical context

**Risk level**: CRITICAL in clinical contexts. A tenfold dose error or daily/BID swap can cause patient harm.

---

## Pattern 17: Confidence Interval Fabrication

**What it looks like**: The LLM generates plausible-looking confidence intervals, p-values, or odds ratios that do not appear in the cited source. Because these values look rigorous, they increase apparent credibility while being entirely fabricated.

**Example**:
```
Claim: "Risk reduction of 23% (95% CI: 15-31%, p<0.001) [Brown et al., 2021]"
Brown et al., 2021: Reports only the point estimate (22%); no CI or p-value reported,
                   or reports CI of 8-38% (different range)
```

**Why it happens**:
- LLMs generate statistically plausible CIs from the point estimate using heuristics
- The CI range looks internally consistent with the point estimate
- Readers rarely verify CI values against source papers

**Detection method**:
1. When inline text includes CI or p-value, search the cited paper for the exact values
2. Flag when specific statistical parameters cannot be located in the source
3. Verify both the width and position of claimed CIs

**Risk level**: HIGH. Fabricated CIs falsely signal rigorous statistical reporting and are rarely checked.

---

## Pattern 18: Secondary Source Attribution

**What it looks like**: Paper A is cited for a claim that Paper A itself sources from Paper B. If Paper B is retracted, flawed, or misinterpreted, the entire chain is compromised. The cited paper is real but is not the primary evidence for the claim.

**Example**:
```
Claim: "The global burden is 2.3 million cases annually [Jones et al., 2020]"
Jones et al., 2020: Cites this figure from WHO 2018 report (which used different methodology)
Actual source: WHO 2018, not Jones 2020
If WHO 2018 figure was revised, Jones' citation perpetuates the old number
```

**Why it happens**:
- LLMs cite the most recent paper mentioning a statistic, not the primary source
- Secondary sources are indexed and easily retrieved; primary sources require tracing
- Citation chains in training data reward proximal over primary sources

**Detection method**:
1. When a cited paper quotes a figure from another source, verify the citation chain
2. Check whether the cited paper's methods section for the specific claim references earlier work
3. When possible, cite the primary source directly

**Risk level**: MEDIUM. The cited paper is real, but the evidence chain may be broken upstream.

---

## Pattern 19: Table/Figure Misread

**What it looks like**: The correct paper is cited and the number cited exists within that paper, but the LLM extracted it from the wrong row, column, subgroup, or condition. The number is real; the attribution within the paper is wrong.

**Example**:
```
Claim: "Sensitivity was 87% in the validation cohort [Park et al., 2022]"
Park et al., 2022, Table 2: Shows 87% in the training cohort (row 1)
                            and 74% in the validation cohort (row 2)
LLM extracted training performance and attributed it to validation
```

**Why it happens**:
- LLMs cannot reliably parse tabular data
- Tables with multiple conditions/subgroups are parsed by row position, not semantic label
- The cited number exists in the paper, so basic content verification passes

**Detection method**:
1. When a specific metric is cited with a population qualifier (validation, subgroup, condition), locate the exact table/figure
2. Verify the value appears in the row/column matching the qualifier
3. Flag when the number exists in the paper but in a different row/subgroup than claimed

**Risk level**: CRITICAL. The paper is real, the number is real, but the clinical interpretation is wrong. Most verification methods miss this entirely.

---

## Pattern 20: Ghost Update

**What it looks like**: The LLM frames a claim with "as of [recent year]" or "recently updated guidelines recommend" while citing a source that predates the claimed update. The temporal framing is fabricated; no update occurred.

**Example**:
```
Claim: "As of 2024, the updated protocol recommends [X] [Guideline Body, 2019]"
Guideline Body, 2019: The guideline was never updated; 2019 version is current
The "as of 2024" framing implies currency that does not exist
```

**Why it happens**:
- LLMs generate temporal qualifiers to signal currency
- Training data contains many "updated in [year]" phrases that reward confident framing
- The underlying citation is real, so the claim passes structural verification

**Detection method**:
1. For any "updated," "as of," or "recently" temporal qualifier, search for a more recent version
2. If no update exists, the temporal framing is fabricated
3. Check guideline-issuing body's current publications page directly

**How to fix**:
1. Remove the temporal qualifier or replace with the actual publication date
2. Search for whether a genuine update was published

**Risk level**: HIGH. Implies current evidence status for potentially outdated recommendations.

---

## Pattern 21: Withdrawn/Corrected Paper Without Notice

**What it looks like**: The cited paper has a published erratum or correction that changes a key finding, but the LLM cites the original uncorrected version. Distinct from Retracted Paper (Pattern 10): the paper was not retracted, only corrected, but the correction matters for the specific claim.

**Example**:
```
Claim: "Sensitivity was reported as 94% [Author et al., 2021]"
Correction notice (2022): Table 3 contained a calculation error; corrected sensitivity is 81%
LLM cites original 94% figure without noting the correction
```

**Why it happens**:
- CrossRef indexes corrections separately from original papers
- LLMs have no access to post-publication correction history
- Corrections are rarely indexed with the same prominence as original papers

**Detection method**:
1. Query CrossRef `update-to` field for corrections and errata (not only retractions)
2. If a correction exists, check whether the corrected value differs from the cited value
3. Flag when a cited specific statistic may have been revised by a published correction

**Risk level**: HIGH in clinical contexts where specific metric values are decision-relevant.

---

## Pattern 22: Self-Referential Loop

**What it looks like**: In RAG (Retrieval-Augmented Generation) systems, the model indexes its own previously generated output and cites it as a source in subsequent generations. The cited "source" is AI-generated text, not an independent publication.

**Example**:
```
Generation 1: LLM generates paragraph citing "studies show 78% efficacy"
This output is indexed in the knowledge base
Generation 2: LLM retrieves Generation 1 and cites it as "recent research"
The 78% figure is now double-laundered through two AI generations
```

**Why it happens**:
- RAG systems index all available documents without distinguishing AI-generated from human-authored
- Generated output may be uploaded to shared knowledge bases or document repositories
- Loop compounds with each generation: fabricated claims gain apparent "citations"

**Detection method**:
1. For RAG systems, audit whether generated content can be written back into the retrieval corpus
2. Check if cited sources can be traced to non-AI-generated primary documents
3. Flag sources that exist only within the organization's internal knowledge base without external verification

**Risk level**: CRITICAL in enterprise RAG systems. Compounds hallucinations across generations without external checks.

---

## Pattern 23: Off-Label Indication Conflation

**What it looks like**: A paper studying Drug/Device X for Indication A is cited as evidence for Drug/Device X in Indication B. The drug and paper are real; the indication is wrong. Distinct from Drug Name Substitution (same drug, wrong indication vs. same indication, wrong drug).

**Example**:
```
Claim: "AI-assisted colonoscopy improves polyp detection in pediatric patients [Kim et al., 2022]"
Kim et al., 2022: Studies adult patients (age 50+) only; pediatric use is off-label
                 and not studied in this paper
```

**Why it happens**:
- LLMs retrieve papers on the drug/device that are topically adjacent
- Indication specificity is a semantic detail that does not affect topic matching
- Training data contains many extrapolations of evidence across indications

**Detection method**:
1. Extract the study population's indication, age group, and setting from the cited paper
2. Compare against the indication being discussed in the inline claim
3. Flag any indication, population, or use-case mismatch

**Risk level**: CRITICAL in medical contexts. Off-label use without evidence can cause patient harm; presenting off-label uses as evidenced is a regulatory and safety issue.

---

## Pattern 24: Survival Bias in Source Selection

**What it looks like**: Across multiple citations in a section, the LLM systematically cites positive trials and landmark studies while omitting null results, negative trials, and replication failures. Each individual citation is valid; the selection creates a misleading picture of the evidence base.

**Example**:
```
Section on AI sepsis detection cites: 3 positive validation studies
Omits: 1 RCT showing no mortality benefit, 2 external validation failures,
       1 commentary on alarm fatigue from the same system
The evidence base appears more favorable than it is
```

**Why it happens**:
- Publication bias is embedded in training data (positive studies are more frequently cited)
- LLMs optimize for claim support, not balanced evidence synthesis
- Negative studies and null results have lower citation counts and reduced retrieval probability

**Detection method**:
1. For any technology or intervention with multiple citations, search for contradictory evidence
2. Check systematic reviews that include heterogeneous findings
3. Flag sections where all citations report positive outcomes without acknowledgment of limitations

**Risk level**: HIGH. Individually valid citations; collectively misleading synthesis. Standard citation checking does not detect this pattern.

---

## Pattern 25: Regulatory Status Mismatch

**What it looks like**: A paper or claim describes an intervention as approved or cleared when it is investigational, or describes approval in one regulatory jurisdiction (EMA, TGA) as if it applies to another (FDA). Real papers are cited, but the regulatory status attributed to the intervention is wrong.

**Example**:
```
Claim: "The FDA-cleared device has demonstrated efficacy in..." [Study et al., 2023]
Study et al., 2023: Published during device's investigational phase, before clearance
                   was granted (or: device is EMA-approved but not FDA-cleared)
```

**Why it happens**:
- Regulatory status changes over time; LLM training data captures one moment
- EMA/FDA/TGA distinctions are subtle and not preserved in training text
- Papers published during investigational phases use language that implies eventual approval

**Detection method**:
1. For any cleared/approved device or drug claim, verify current regulatory status at primary source (accessdata.fda.gov, EMA EPAR)
2. Confirm jurisdiction of cited approval matches the jurisdiction of the claim
3. Check whether cited study predates or postdates the approval event

**Risk level**: HIGH. Presenting investigational interventions as approved constitutes a regulatory compliance failure in clinical decision support contexts.

---

## Prevention Strategies

For AI-assisted writing:
- Run all five verification phases before publication
- Prioritize Phase 2 (content alignment) over Phase 1 (URL checks)
- Use retrieval-augmented generation with citation databases
- Require human verification of all references
- Stratify risk by topic familiarity (less-studied topics have higher fabrication rates)

For manual writing:
- Copy DOIs directly from source
- Verify claim strength matches study design
- Check retraction status for older citations
- Double-check after any editing
- Run batch verification before submission

For system design:
- Implement retraction database checks in citation pipelines
- Add study design classification to content extraction
- Detect and flag causal language paired with observational designs
- Track fabrication rates by topic area for risk stratification
