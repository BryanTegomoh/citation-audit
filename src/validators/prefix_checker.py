"""DOI prefix validation and publisher identification."""

import json
import re
from pathlib import Path
from typing import Optional, Dict


# Default publisher prefixes (subset - full list in data/publisher_prefixes.json)
DEFAULT_PREFIXES: Dict[str, str] = {
    # Major medical publishers
    "10.1038": "Nature/Springer Nature",
    "10.1056": "NEJM (Massachusetts Medical Society)",
    "10.1001": "JAMA Network (AMA)",
    "10.1016": "Elsevier",
    "10.1136": "BMJ Publishing",
    "10.1093": "Oxford University Press",
    "10.1371": "PLOS",
    "10.1126": "Science (AAAS)",
    "10.1161": "American Heart Association",
    "10.1002": "Wiley",
    "10.1007": "Springer",
    "10.1097": "Wolters Kluwer",
    "10.1177": "SAGE Publications",
    "10.1080": "Taylor & Francis",

    # Medical specialty publishers
    "10.1148": "Radiological Society of North America",
    "10.2196": "JMIR Publications",
    "10.1158": "AACR (Cancer Research)",
    "10.1200": "ASCO (JCO)",
    "10.1212": "American Academy of Neurology",
    "10.1542": "American Academy of Pediatrics",
    "10.1164": "American Thoracic Society",
    "10.1183": "European Respiratory Society",
    "10.1172": "American Society for Clinical Investigation",

    # Preprint servers
    "10.1101": "bioRxiv/medRxiv (Cold Spring Harbor)",
    "10.48550": "arXiv",
    "10.2139": "SSRN",

    # Other major publishers
    "10.3389": "Frontiers",
    "10.1073": "PNAS",
    "10.1186": "BioMed Central/Springer Nature",
    "10.3390": "MDPI",
    "10.1109": "IEEE",
    "10.1145": "ACM",
    "10.7554": "eLife",
}

# Journal name to expected prefix mapping
JOURNAL_PREFIXES: Dict[str, str] = {
    # Nature family
    "nature": "10.1038",
    "nature medicine": "10.1038",
    "nature communications": "10.1038",
    "scientific reports": "10.1038",

    # NEJM
    "new england journal of medicine": "10.1056",
    "nejm": "10.1056",

    # JAMA family
    "jama": "10.1001",
    "jama internal medicine": "10.1001",
    "jama network open": "10.1001",
    "jama oncology": "10.1001",
    "jama cardiology": "10.1001",
    "jama neurology": "10.1001",
    "jama pediatrics": "10.1001",
    "jama surgery": "10.1001",

    # Lancet family
    "lancet": "10.1016",
    "the lancet": "10.1016",
    "lancet oncology": "10.1016",
    "lancet digital health": "10.1016",

    # BMJ family
    "bmj": "10.1136",
    "gut": "10.1136",
    "heart": "10.1136",
    "thorax": "10.1136",

    # Science
    "science": "10.1126",
    "science translational medicine": "10.1126",

    # PLOS
    "plos medicine": "10.1371",
    "plos one": "10.1371",

    # Cell family
    "cell": "10.1016",

    # Circulation family
    "circulation": "10.1161",
    "circulation research": "10.1161",

    # Radiology
    "radiology": "10.1148",
    "radiographics": "10.1148",

    # Neurology
    "neurology": "10.1212",

    # Pediatrics
    "pediatrics": "10.1542",

    # JCI
    "journal of clinical investigation": "10.1172",
    "jci": "10.1172",
}

# Cache for loaded prefix data
_prefix_cache: Optional[Dict[str, str]] = None


def _load_prefixes() -> Dict[str, str]:
    """Load publisher prefixes from data file or use defaults."""
    global _prefix_cache

    if _prefix_cache is not None:
        return _prefix_cache

    # Try to load from data file
    data_file = Path(__file__).parent.parent.parent / "data" / "publisher_prefixes.json"

    if data_file.exists():
        try:
            with open(data_file, 'r', encoding='utf-8') as f:
                _prefix_cache = json.load(f)
                return _prefix_cache
        except (json.JSONDecodeError, IOError):
            pass

    # Fall back to defaults
    _prefix_cache = DEFAULT_PREFIXES
    return _prefix_cache


def extract_prefix(doi: str) -> Optional[str]:
    """Extract the registrant prefix from a DOI.

    Args:
        doi: A DOI string (with or without URL prefix)

    Returns:
        The prefix (e.g., "10.1038") or None if invalid
    """
    # Clean the DOI
    doi = doi.strip()
    if doi.startswith('http'):
        doi = doi.split('doi.org/')[-1]

    # Extract prefix (everything up to and including the slash)
    match = re.match(r'(10\.\d{4,})/', doi)
    if match:
        return match.group(1)

    return None


def get_publisher_for_prefix(prefix: str) -> Optional[str]:
    """Get the publisher name for a DOI prefix.

    Args:
        prefix: DOI prefix (e.g., "10.1038")

    Returns:
        Publisher name or None if unknown
    """
    prefixes = _load_prefixes()
    return prefixes.get(prefix)


def get_expected_prefix_for_journal(journal_name: str) -> Optional[str]:
    """Get the expected DOI prefix for a journal.

    Args:
        journal_name: Journal name (case-insensitive)

    Returns:
        Expected DOI prefix or None if unknown
    """
    journal_lower = journal_name.lower().strip()
    return JOURNAL_PREFIXES.get(journal_lower)


def validate_prefix(doi: str, claimed_journal: Optional[str] = None) -> dict:
    """Validate that a DOI's prefix matches the claimed journal.

    Args:
        doi: The DOI to validate
        claimed_journal: The journal name claimed in the citation

    Returns:
        Dict with validation results
    """
    prefix = extract_prefix(doi)

    result = {
        'doi': doi,
        'prefix': prefix,
        'publisher': None,
        'expected_prefix': None,
        'prefix_valid': True,
        'journal_match': None,
        'issues': [],
    }

    if not prefix:
        result['prefix_valid'] = False
        result['issues'].append(f"Could not extract prefix from DOI: {doi}")
        return result

    # Get publisher for this prefix
    result['publisher'] = get_publisher_for_prefix(prefix)

    if not result['publisher']:
        result['issues'].append(f"Unknown publisher prefix: {prefix}")

    # Check if prefix matches claimed journal
    if claimed_journal:
        expected = get_expected_prefix_for_journal(claimed_journal)
        result['expected_prefix'] = expected

        if expected:
            result['journal_match'] = (prefix == expected)

            if not result['journal_match']:
                result['prefix_valid'] = False
                result['issues'].append(
                    f"Prefix mismatch: DOI has {prefix} ({result['publisher']}), "
                    f"but {claimed_journal} should have {expected}"
                )

    return result


def get_all_prefixes() -> Dict[str, str]:
    """Get all known publisher prefixes.

    Returns:
        Dict mapping prefix to publisher name
    """
    return _load_prefixes().copy()
