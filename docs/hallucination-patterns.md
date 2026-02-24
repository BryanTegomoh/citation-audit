# Citation Hallucination Patterns

This document describes the six main patterns of citation hallucination found in AI-generated and human-written academic content. Understanding these patterns helps you recognize and fix citation errors.

## Overview

Citation hallucinations occur when the metadata in a citation (author names, year, title, DOI) doesn't match reality. These errors range from minor (wrong year) to severe (completely fabricated papers).

| Pattern | Severity | Detection Difficulty | Frequency |
|---------|----------|---------------------|-----------|
| Valid DOI, Wrong Paper | Critical | Medium | Common |
| Non-Existent DOI | High | Easy | Common |
| Wrong Metadata | Medium | Medium | Very Common |
| Completely Fabricated | Critical | Easy-Medium | Occasional |
| Wrong Publisher Prefix | Medium | Easy | Occasional |
| Memory-Constructed URL | Critical | Easy (post-hoc) | Common for non-DOI links |

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
```

If multiple checks fail, the citation is likely Pattern 4 (completely fabricated).

## Why AI Generates These Errors

Large language models generate citations by:

1. **Pattern completion**: Generating DOI-like strings that follow observed patterns
2. **Semantic plausibility**: Creating author names and titles that sound reasonable
3. **Statistical likelihood**: Combining common elements (journal names, years, topics)

The model doesn't have access to the actual DOI database, so it can't verify that generated DOIs exist or point to the claimed papers.

## Prevention Strategies

For AI-assisted writing:
- Always verify DOIs before final submission
- Use retrieval-augmented generation (RAG) with citation databases
- Require human verification of all references

For manual writing:
- Copy DOIs directly from source
- Double-check after any editing
- Run batch verification before submission
