# Citation Verification Workflow

This guide provides step-by-step instructions for verifying citations, suitable for both manual checking and understanding automated verification.

## Quick Verification Checklist

Use this checklist for each citation:

- [ ] DOI resolves (not 404)
- [ ] Author names match (at least first author's last name)
- [ ] Publication year matches (within 1 year)
- [ ] Journal/source matches DOI prefix
- [ ] Title is related to claimed content

## Manual Verification Process

### Step 1: Extract the DOI

Find the DOI in your citation. Common formats:

```
https://doi.org/10.1038/s41591-020-1034-x
doi:10.1038/s41591-020-1034-x
DOI: 10.1038/s41591-020-1034-x
```

The DOI is everything after "10." (e.g., `10.1038/s41591-020-1034-x`)

### Step 2: Test DOI Resolution

**Method A: Browser**
1. Go to `https://doi.org/YOUR_DOI_HERE`
2. If it redirects to a paper, the DOI exists
3. If you get a 404 error, the DOI is invalid

**Method B: Command Line**
```bash
curl -I https://doi.org/10.1038/s41591-020-1034-x
```
- Status 302/303 = Valid (redirects to paper)
- Status 404 = Invalid DOI

### Step 3: Compare Metadata

If the DOI resolves, compare the actual paper against your citation:

**Get metadata from CrossRef:**
```
https://api.crossref.org/works/10.1038/s41591-020-1034-x
```

Or use a user-friendly tool:
- [CrossRef Metadata Search](https://search.crossref.org/)
- Enter the DOI to see actual title, authors, year

**Compare:**
| Field | Your Citation | Actual Paper |
|-------|---------------|--------------|
| First Author | | |
| Year | | |
| Title (gist) | | |
| Journal | | |

### Step 4: Check Publisher Prefix

The DOI prefix (before the `/`) identifies the publisher:

| If citation claims | DOI prefix should be |
|-------------------|---------------------|
| Nature journals | 10.1038 |
| JAMA Network | 10.1001 |
| NEJM | 10.1056 |
| Lancet | 10.1016 |
| BMJ | 10.1136 |
| PLOS | 10.1371 |
| Science | 10.1126 |

See [doi-reference.md](doi-reference.md) for complete list.

### Step 5: Determine Verification Status

Based on your checks:

| Result | Status | Action |
|--------|--------|--------|
| All match | VALID | No action needed |
| DOI 404 | INVALID | Find correct DOI or paper |
| Wrong paper | MISMATCH | Find correct DOI |
| Year off by 1 | WARNING | Consider updating |
| Author variant | WARNING | Minor, usually OK |
| Wrong journal | INVALID | Wrong DOI or wrong journal name |

## Decision Tree

```
START: Have DOI?
│
├── No → Search for paper, find DOI, restart
│
└── Yes → Does DOI resolve?
    │
    ├── No (404) → INVALID: DOI doesn't exist
    │             → Action: Find correct DOI or verify paper exists
    │
    └── Yes → Does paper match citation?
        │
        ├── No match at all → Pattern 1: Wrong Paper
        │                   → Action: Find correct DOI
        │
        └── Partial match → Check details:
            │
            ├── Author wrong → Pattern 3: Wrong Metadata
            │                → Action: Update citation text
            │
            ├── Year wrong → Pattern 3: Wrong Metadata
            │              → Action: Use year from DOI
            │
            └── Prefix wrong → Pattern 5: Wrong Publisher
                            → Action: Verify journal name
```

## Batch Verification Strategy

For documents with many citations:

### Prioritization

Check high-risk citations first:
1. Citations supporting critical claims
2. Citations with unusual or new journals
3. Citations from very recent years (2023-2024)
4. Citations with complex DOIs or long suffixes

### Sampling Approach

For large documents (100+ citations):
1. Verify all citations in abstract and conclusions
2. Random sample 20% of remaining citations
3. If error rate > 5%, verify all remaining
4. If error rate < 2%, sampling is sufficient

### Automated + Manual Hybrid

1. Run automated verification on all citations
2. Manually review all flagged issues
3. Spot-check 10% of "valid" citations
4. Focus manual effort on ambiguous cases

## Fixing Common Issues

### DOI Returns 404

1. Search Google Scholar for: `"exact paper title"`
2. Search PubMed for: `author name AND keyword`
3. Check if paper was retracted (search "retraction" + title)
4. Paper may be preprint-only (check arXiv, bioRxiv)

### DOI Points to Wrong Paper

1. You have wrong DOI but right paper exists:
   - Find paper on publisher site
   - Get correct DOI from paper page

2. Paper might not exist:
   - Verify authors published in that area
   - Search for similar papers as replacement

### Author Name Mismatch

Common acceptable variations:
- First name vs initials: "John Smith" vs "J. Smith"
- Middle name included/excluded
- Hyphenated names
- Transliteration differences

Flag if first author's last name is completely different.

### Year Mismatch

Acceptable: Citation says 2020, DOI says 2021
- Papers published online Dec 2020 often assigned 2021
- Allow ±1 year tolerance

Not acceptable: Citation says 2020, DOI says 2015
- Likely wrong paper or major error

## Quality Assurance Levels

### Level 1: Basic (Fast)
- DOI resolution check only
- Catches Pattern 2 (non-existent DOIs)
- ~1 second per citation

### Level 2: Standard (Recommended)
- DOI resolution + CrossRef metadata
- Catches Patterns 1, 2, 3, 5
- ~2-3 seconds per citation

### Level 3: Thorough (Pre-Publication)
- All Level 2 checks
- Manual title/topic verification
- Author affiliation check
- Catches all patterns including Pattern 4
- ~30-60 seconds per citation

## Verification Report Template

For documenting your verification:

```markdown
## Citation Verification Report

**Document**: [filename]
**Date**: [date]
**Verifier**: [name]

### Summary
- Total citations: X
- Verified: X
- Issues found: X
- Error rate: X%

### Issues Found

#### Issue 1
- **Citation**: [text]
- **DOI**: [doi]
- **Problem**: [description]
- **Resolution**: [what was done]

[Repeat for each issue]

### Notes
[Any general observations]
```

## When to Re-Verify

- After any editing of citations
- Before journal submission
- After co-author additions
- After AI assistance used
- Annually for living documents
