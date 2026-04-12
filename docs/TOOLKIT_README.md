# Citation Audit - CLI Toolkit

Detect and fix citation errors in academic and medical literature. This toolkit helps researchers, writers, and developers identify citations where DOIs don't exist, point to the wrong papers, or have incorrect metadata.

## The Problem

Academic writing frequently contains citation errors:

- **Valid DOI, Wrong Paper**: DOI exists but resolves to a completely different paper
- **Non-Existent DOI**: DOI follows correct syntax but returns 404
- **Wrong Metadata**: DOI is correct but author/year in citation text is wrong
- **Completely Fabricated**: Paper, authors, and journal don't exist
- **Wrong Publisher**: DOI prefix doesn't match claimed journal

These errors undermine credibility and can propagate misinformation. This toolkit helps catch them before publication.

## Installation

```bash
# Clone or copy this folder
cd citation-audit

# Install dependencies
pip install -r requirements.txt

# Or install as a package
pip install -e .
```

## Quick Start

### Verify a single DOI

```bash
python -m citation_toolkit verify 10.1038/s41591-020-1034-x
```

Output:
```
DOI: 10.1038/s41591-020-1034-x
Status: VALID
Title: Reporting guidelines for clinical trial reports...
Authors: Liu X, Cruz Rivera S, Moher D, et al.
Year: 2020
Journal: Nature Medicine
```

### Check all citations in a document

```bash
python -m citation_toolkit check my_paper.md --output report.md
```

### Batch verify a list of DOIs

```bash
python -m citation_toolkit batch dois.txt --output report.md
```

### Extract citations without verifying

```bash
python -m citation_toolkit extract document.md
```

## Input Formats Supported

| Format | Extension | Description |
|--------|-----------|-------------|
| Markdown | `.md`, `.qmd` | Extracts DOIs from hyperlinks and inline citations |
| BibTeX | `.bib` | Parses standard BibTeX entries |
| Plain text | `.txt` | One DOI per line |

## What Gets Checked

For each citation, the toolkit:

1. **Resolves the DOI** - Confirms it exists (not 404)
2. **Fetches metadata** - Gets actual title, authors, year from CrossRef
3. **Compares claimed vs actual** - Flags mismatches in author names or publication year
4. **Validates publisher prefix** - Checks if DOI prefix matches claimed journal

## Output Report

The verification report (Markdown format) shows:

- Total citations checked
- Number of errors by type
- Detailed findings for each problematic citation
- Suggested fixes where possible

See [examples/sample_report.md](examples/sample_report.md) for a sample output.

## Documentation

- [Hallucination Patterns](hallucination-patterns.md) - 33 citation error patterns across 3 tiers
- [Verification Workflow](docs/verification-workflow.md) - Manual verification steps
- [DOI Reference](docs/doi-reference.md) - Understanding DOI structure and publisher prefixes
- [Case Studies](docs/case-studies.md) - Real examples of caught errors

## No API Keys Required

This toolkit uses only free, unauthenticated APIs:

- **CrossRef API** - Paper metadata lookup (rate limit: ~50 req/sec)
- **DOI.org** - DOI resolution checking

## Project Structure

```
citation-audit/
├── README.md                 # Project overview (56 failure modes)
├── CONTRIBUTING.md           # Contribution guidelines
├── requirements.txt          # Python dependencies
├── setup.py                  # Package installation
├── Makefile                  # Common commands
│
├── scripts/                  # Verification pipeline scripts
│   ├── verification_pipeline.py   # Main orchestrator (all phases)
│   ├── citation_extractor.py      # Citation extraction from markdown
│   ├── doi_validator.py           # Phase 0: CrossRef API validation
│   ├── url_verifier.py            # Phase 1: HTTP status checking
│   ├── content_verifier.py        # Phase 2: Content-claim alignment
│   ├── semantic_verifier.py       # Phase 2+: Scope, causality, retraction
│   ├── metadata_verifier.py       # Phase 3: Metadata + retraction
│   ├── rubric.py                  # Multi-dimensional rubric scoring
│   └── coding_audit.py            # E/M, CPT, ICD-10 coding audit
│
├── src/                      # CLI source code
│   ├── cli.py               # Command-line interface
│   ├── verify.py            # Core verification logic
│   ├── coding_verifier.py   # Medical coding verification
│   ├── extractors/          # Citation extraction (markdown, BibTeX, plaintext)
│   ├── validators/          # DOI validation (CrossRef, resolver, prefix)
│   └── reporters/           # Report generation
│
├── data/                     # Reference data
│   ├── publisher_prefixes.json    # 90+ publisher DOI prefixes
│   └── journal_patterns.json      # Journal name to prefix mapping
│
├── docs/                     # Documentation
│   ├── METHODOLOGY.md             # Full methodology (56 failure modes)
│   ├── hallucination-patterns.md  # 33 patterns with examples
│   ├── verification-workflow.md   # Manual + automated workflows
│   ├── doi-reference.md           # DOI structure, 90+ publisher prefixes
│   ├── case-studies.md            # Real-world audit examples
│   └── supplementary/             # Correction log, proposals
│
├── papers/                   # Research manuscripts
├── reports/                  # Audit reports
├── examples/                 # Sample files
└── tests/                    # Unit tests (5 test files)
```

## Use Cases

- **Before publishing**: Verify all citations in a manuscript
- **Content review**: Check literature reviews for citation errors
- **Quality assurance**: Automated CI/CD checks for documentation
- **Research integrity**: Audit existing publications for citation accuracy

## Limitations

- Only works with DOI-based citations (not all papers have DOIs)
- Cannot verify claims made in the citing text (only that the paper exists)
- Rate limited by CrossRef API (be patient with large batches)
- Some older papers may have incomplete metadata in CrossRef

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on improving this toolkit.

## License

MIT License - Use freely, attribution appreciated.

## Origin

This toolkit was developed after auditing 800+ DOIs in a medical AI handbook, where we discovered ~3% of citations had significant errors. The patterns and detection methods documented here come from that real-world experience.
