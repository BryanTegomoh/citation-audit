# DOI Reference Guide

This document explains DOI structure, publisher prefixes, and common patterns to help identify citation issues.

## What is a DOI?

A Digital Object Identifier (DOI) is a persistent identifier for digital content. For academic papers, DOIs provide a stable way to link to publications even if URLs change.

**Format**: `10.PREFIX/SUFFIX`

**Example**: `10.1038/s41591-020-1034-x`
- `10.` = Required DOI indicator
- `1038` = Registrant code (Nature/Springer Nature)
- `/` = Separator
- `s41591-020-1034-x` = Suffix (publisher-specific)

## DOI Anatomy

```
10.1038/s41591-020-1034-x
│  │    │
│  │    └── Suffix: Identifies specific item
│  │        (format varies by publisher)
│  │
│  └── Prefix: Identifies registrant (publisher)
│      (always starts with 10.)
│
└── DOI indicator (always "10.")
```

## Major Publisher Prefixes

### Medical and Scientific Publishers

| Prefix | Publisher | Major Journals |
|--------|-----------|----------------|
| 10.1038 | Springer Nature | Nature, Nature Medicine, Scientific Reports |
| 10.1056 | Massachusetts Medical Society | NEJM |
| 10.1001 | American Medical Association | JAMA, JAMA Network Open |
| 10.1016 | Elsevier | Lancet, Cell, many others |
| 10.1136 | BMJ Publishing | BMJ, Heart, Gut |
| 10.1093 | Oxford University Press | many journals |
| 10.1371 | Public Library of Science | PLOS ONE, PLOS Medicine |
| 10.1126 | AAAS | Science, Science Translational Medicine |
| 10.1161 | American Heart Association | Circulation, Stroke |
| 10.1002 | Wiley | many journals |
| 10.1007 | Springer | many journals |
| 10.1097 | Wolters Kluwer | Annals of Surgery, many others |
| 10.1177 | SAGE | many journals |
| 10.1080 | Taylor & Francis | many journals |

### Specialty Medical Publishers

| Prefix | Publisher | Major Journals |
|--------|-----------|----------------|
| 10.1148 | Radiological Society | Radiology, RadioGraphics |
| 10.2196 | JMIR Publications | JMIR, JMIR Medical Informatics |
| 10.1158 | AACR | Cancer Research, Clinical Cancer Research |
| 10.1200 | ASCO | JCO, JCO Precision Oncology |
| 10.1212 | AAN | Neurology |
| 10.1542 | AAP | Pediatrics |
| 10.1164 | ATS | AJRCCM |
| 10.1183 | ERS | ERJ |
| 10.1053 | Elsevier (Gastro) | Gastroenterology |
| 10.1172 | ASCI | JCI |

### Preprint Servers

| Prefix | Server |
|--------|--------|
| 10.1101 | bioRxiv, medRxiv |
| 10.48550 | arXiv |
| 10.2139 | SSRN |

### Multi-Journal Publishers (Variable Suffixes)

Some publishers use different suffix patterns for different journals:

**Elsevier (10.1016)**:
- Lancet: `10.1016/S0140-6736(XX)XXXXX-X`
- Cell: `10.1016/j.cell.XXXX.XX.XXX`
- Journal articles: `10.1016/j.JOURNALABBREV.XXXX.XX.XXX`

**Springer Nature (10.1038)**:
- Nature: `10.1038/sXXXXX-XXX-XXXXX-X`
- Nature Medicine: `10.1038/s41591-XXX-XXXX-X`
- Scientific Reports: `10.1038/s41598-XXX-XXXXX-X`

## DOI Suffix Patterns

### Nature/Springer Nature Pattern
```
10.1038/s41591-020-1034-x
        │     │    │    │
        │     │    │    └── Check character (alphanumeric)
        │     │    └── Article number
        │     └── Year
        └── Journal identifier (41591 = Nature Medicine)
```

### JAMA Network Pattern
```
10.1001/jamanetworkopen.2023.12345
        │                │     │
        │                │     └── Article number
        │                └── Year
        └── Journal name
```

### Elsevier Pattern
```
10.1016/j.cell.2023.01.001
        │ │    │    │  │
        │ │    │    │  └── Article sequence
        │ │    │    └── Month
        │ │    └── Year
        │ └── Journal abbreviation
        └── Format indicator
```

## Common DOI Errors

### Invalid Characters
DOIs can contain: `a-z`, `A-Z`, `0-9`, `-`, `.`, `_`, `/`

Invalid examples:
- `10.1038/s41591-020-1034-x ` (trailing space)
- `10.1038/s41591–020–1034–x` (em dashes instead of hyphens)
- `10.1038\s41591-020-1034-x` (backslash instead of forward slash)

### Common Typos
- Missing digit: `10.138/...` instead of `10.1038/...`
- Wrong year in suffix: `10.1038/s41591-2020-1034-x` vs `10.1038/s41591-020-1034-x`
- Transposed characters: `10.1038/s41951-...` vs `10.1038/s41591-...`

### URL Encoding Issues
DOIs in URLs should be encoded:
- `<` becomes `%3C`
- `>` becomes `%3E`
- Spaces become `%20` or `+`

When extracting DOIs from URLs, decode first.

## Verifying DOI Prefix-Journal Match

### Quick Reference

If someone cites **Nature Medicine**, the DOI must start with **10.1038**.

If someone cites **JAMA**, the DOI must start with **10.1001**.

If the prefix doesn't match, either:
1. The DOI is wrong
2. The journal name is wrong
3. The citation is fabricated

### Journal-to-Prefix Lookup

| Journal | Expected Prefix |
|---------|----------------|
| Nature Medicine | 10.1038 |
| NEJM | 10.1056 |
| JAMA | 10.1001 |
| Lancet | 10.1016 |
| BMJ | 10.1136 |
| Science | 10.1126 |
| Cell | 10.1016 |
| PLOS Medicine | 10.1371 |
| Annals of Internal Medicine | 10.7326 |
| Circulation | 10.1161 |
| Radiology | 10.1148 |

## Testing DOI Resolution

### Via Web Browser
Visit: `https://doi.org/YOUR_DOI`

Examples:
- Valid: https://doi.org/10.1038/s41591-020-1034-x → Redirects to Nature
- Invalid: https://doi.org/10.1038/s99999-999-9999-x → 404 Error

### Via Command Line

```bash
# Check if DOI exists (look for redirect)
curl -I https://doi.org/10.1038/s41591-020-1034-x

# Get metadata as JSON
curl "https://api.crossref.org/works/10.1038/s41591-020-1034-x"
```

### Via CrossRef API

```python
import requests

doi = "10.1038/s41591-020-1034-x"
response = requests.get(f"https://api.crossref.org/works/{doi}")

if response.status_code == 200:
    data = response.json()["message"]
    print(f"Title: {data['title'][0]}")
    print(f"Authors: {data['author']}")
    print(f"Year: {data['published']['date-parts'][0][0]}")
else:
    print("DOI not found")
```

## Special Cases

### Preprints

Preprints (bioRxiv, medRxiv, arXiv) have DOIs but may later get a different DOI when published in a journal. Both DOIs remain valid.

Example:
- Preprint: `10.1101/2020.01.01.123456`
- Published: `10.1038/s41591-020-XXXXX-X`

### Supplementary Materials

Some publishers assign separate DOIs to supplementary materials. These are valid but different from the main article DOI.

### Corrections and Retractions

- Corrections get their own DOIs
- Retracted papers' DOIs still resolve but should show retraction notice
- DOIs are never deleted (persistence principle)

### Conference Proceedings

Conference papers often have DOIs from:
- IEEE: `10.1109/...`
- ACM: `10.1145/...`
- Springer LNCS: `10.1007/978-...`

These are valid publications but different from journal articles.

## Resources

- [DOI Handbook](https://www.doi.org/doi_handbook/TOC.html)
- [CrossRef REST API](https://api.crossref.org/)
- [DOI Registration Agencies](https://www.doi.org/registration_agencies.html)
