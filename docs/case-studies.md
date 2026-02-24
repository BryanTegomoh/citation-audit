# Case Studies: Real Citation Errors

These anonymized case studies illustrate actual citation errors discovered during document audits. Each demonstrates a hallucination pattern and how it was detected and fixed.

## Case Study 1: The Wrong Paper Problem

**Pattern**: Valid DOI, Wrong Paper

### The Citation
```markdown
AI systems can achieve diagnostic accuracy comparable to specialists
([Martinez et al., 2020](https://doi.org/10.1038/s41591-019-0649-9)).
```

### The Discovery

When verifying this DOI, the CrossRef API returned:
```json
{
  "title": "Dermatologist-level classification of skin cancer",
  "author": [{"family": "Esteva", "given": "Andre"}, ...],
  "published": {"date-parts": [[2017, 1, 25]]}
}
```

**Problems identified**:
- Author mismatch: "Martinez et al." vs "Esteva et al."
- Year mismatch: 2020 vs 2017
- Title mismatch: General AI diagnostics vs specific skin cancer paper

### The Fix

1. Searched for actual "Martinez et al., 2020" paper on AI diagnostics
2. Found correct paper: "Deep learning for diagnosis..." in BMJ
3. Correct DOI: `10.1136/bmj.m689`
4. Updated citation

### Lesson Learned

The DOI existed and resolved to a legitimate, highly-cited paper about AI in medicine. Basic validation would pass. Only metadata comparison caught the error.

---

## Case Study 2: The Non-Existent DOI

**Pattern**: Non-Existent DOI (404)

### The Citation
```markdown
Early expert systems achieved 90% accuracy in diagnosis
([Thompson, 1976](https://doi.org/10.1016/0010-4809(76)90009-0)).
```

### The Discovery

```bash
$ curl -I https://doi.org/10.1016/0010-4809(76)90009-0
HTTP/2 404
```

The DOI format looked valid (correct Elsevier prefix, plausible pattern), but it didn't exist.

### Investigation

1. Searched for papers by Thompson in 1976 on expert systems
2. Found the actual paper was published in 1975, not 1976
3. Correct DOI: `10.1016/0010-4809(75)90009-9`

The AI had generated a plausible DOI by incrementing the year in the pattern, but this created a non-existent DOI.

### The Fix

1. Changed year from 1976 to 1975
2. Updated DOI suffix from `(76)` to `(75)`
3. Verified new DOI resolves correctly

### Lesson Learned

DOI suffixes often contain encoded years. Off-by-one year errors can create DOIs that look valid but don't exist.

---

## Case Study 3: The Fabricated Authority

**Pattern**: Completely Fabricated Citation

### The Citation
```markdown
Regional treatment variations affected outcomes significantly
([Williams et al., 2021](https://doi.org/10.1038/s41591-2021-01464-x)).
```

### The Discovery

Multiple red flags:
1. DOI returned 404
2. "Williams et al., 2021" search returned no relevant papers
3. DOI suffix pattern was unusual for Nature Medicine

### Investigation

1. Searched CrossRef for similar DOIs: found `10.1038/s41591-021-01614-0` existed
2. That paper was by Rajpurkar et al. on a different topic
3. No paper matching the claimed content existed

### The Fix

1. Identified what claim needed support (regional treatment variations)
2. Found actual research on the topic: meta-analysis from Scientific Reports
3. Replaced with valid citation: `([Chen et al., 2021](https://doi.org/10.1038/s41598-021-84973-5))`
4. Verified new citation actually supported the claim

### Lesson Learned

When a DOI fails AND author search fails, the entire citation is likely fabricated. Need to find real supporting evidence or remove the claim.

---

## Case Study 4: The Year Confusion

**Pattern**: Wrong Metadata (Year)

### The Citation
```markdown
Physician burnout affects patient safety
([Anderson et al., 2016](https://doi.org/10.4065/mcp.2015.0635)).
```

### The Discovery

CrossRef metadata returned:
```json
{
  "author": [{"family": "Anderson", "given": "J."}, ...],
  "published": {"date-parts": [[2015, 12, 1]]}
}
```

The DOI suffix contained "2015" but citation claimed "2016".

### Investigation

- Paper was published online December 2015
- Some databases list it as 2016 (January issue)
- The DOI suffix definitively shows 2015

### The Fix

Updated citation year from 2016 to 2015 to match DOI metadata.

### Lesson Learned

Publication dates can be ambiguous. Trust the DOI metadata (from CrossRef) as authoritative.

---

## Case Study 5: The Publisher Mismatch

**Pattern**: Wrong Publisher Prefix

### The Citation
```markdown
AI mammography trials showed 20% reduction in false positives
([Brown et al., 2023](https://doi.org/10.1001/jamaoncol.2023.2018)).
```

### The Discovery

Text claimed this was from "Lancet Oncology" but:
- DOI prefix `10.1001` = JAMA Network
- `jamaoncol` in suffix = JAMA Oncology specifically

### Investigation

1. The paper at this DOI was real but was from JAMA Oncology
2. The same research group had published in Lancet Oncology with different findings
3. AI had mixed up the publications

### The Fix

Two options:
1. Keep DOI, change "Lancet Oncology" to "JAMA Oncology"
2. Find the actual Lancet Oncology paper if that was intended

Chose option 2 after verifying which paper supported the specific claim.

### Lesson Learned

Publisher prefix is a quick first check. JAMA (10.1001) ≠ Lancet (10.1016).

---

## Case Study 6: The Hospital Name Error

**Pattern**: Wrong Details (Non-DOI)

### The Citation
```markdown
Memorial Hospital (Seattle) found concordance rates below 50%
([Internal Report, 2019](https://doi.org/10.xxxxx)).
```

### The Discovery

- The cited hospital was actually in a different city
- The concordance rate was 80%, not below 50%
- The date was 2018, not 2019

### Investigation

The AI had combined:
- A real hospital name (but wrong location)
- A real study finding (but wrong value)
- A plausible year (but wrong)

### The Fix

1. Found actual source: different hospital, different findings
2. Rewrote sentence to accurately reflect real research
3. Updated citation to match

### Lesson Learned

Non-DOI elements (institution names, specific numbers) can also be hallucinated. Verify the complete claim, not just the DOI.

---

## Common Patterns Across Cases

### Red Flags That Warranted Investigation

1. DOI suffix containing year that doesn't match citation year
2. DOI prefix not matching claimed journal's publisher
3. Author name not appearing in first few CrossRef results
4. Very recent citations (easier for AI to hallucinate)
5. Specific quantitative claims (percentages, sample sizes)

### Verification Steps That Caught Errors

1. **DOI Resolution**: Caught Cases 2, 3
2. **Metadata Comparison**: Caught Cases 1, 4
3. **Prefix Validation**: Caught Case 5
4. **Content Verification**: Caught Case 6

### Time Investment

| Verification Level | Time per Citation | Errors Caught |
|--------------------|-------------------|---------------|
| DOI Resolution Only | 2 seconds | ~30% |
| + Metadata Check | 10 seconds | ~80% |
| + Content Verification | 60 seconds | ~95% |
| Full Manual Review | 3-5 minutes | ~100% |

## Recommendations

Based on these cases:

1. **Never skip DOI resolution** - It's fast and catches obvious errors
2. **Always check first author's last name** - Most reliable metadata field
3. **Verify prefix matches journal** - Quick sanity check
4. **Be suspicious of recent citations** - Higher hallucination rate
5. **Verify quantitative claims separately** - Numbers are often wrong even when papers exist
6. **Document your fixes** - Future audits benefit from your work
