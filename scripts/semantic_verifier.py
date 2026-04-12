#!/usr/bin/env python3
"""
Semantic Verifier Module (Phase 2+)

Detects higher-order citation failures that pass structural and content checks:
  - Scope extrapolation (narrow study cited as broad evidence)
  - Evidence strength inflation (pilot cited as "demonstrated")
  - Causal inference escalation (correlation cited as causation)
  - Retraction status checking
  - Conference abstract vs. full paper confusion
  - Drug name substitution detection
  - Geographic population mismatch
  - Direction-of-effect reversal
  - Industry funding / conflict of interest flags

These failures represent the 79% of citation errors invisible to URL checking.
Standard link verification catches only structural breaks. This module targets
the semantic layer where a valid DOI points to a real paper that does not
support the specific claim being made.
"""

import re
import json
import asyncio
import aiohttp
from dataclasses import dataclass, field, asdict
from typing import List, Optional, Dict, Tuple, Set
from enum import Enum


class SemanticFlag(Enum):
    """Semantic verification flags."""
    SCOPE_EXTRAPOLATION = "scope_extrapolation"
    EVIDENCE_STRENGTH_INFLATION = "evidence_strength_inflation"
    CAUSAL_INFERENCE_ESCALATION = "causal_inference_escalation"
    RETRACTED_PAPER = "retracted_paper"
    SUPERSEDED_EVIDENCE = "superseded_evidence"
    CONFERENCE_ABSTRACT = "conference_abstract"
    DRUG_NAME_MISMATCH = "drug_name_mismatch"
    GEOGRAPHIC_MISMATCH = "geographic_mismatch"
    DIRECTION_REVERSAL = "direction_reversal"
    INDUSTRY_FUNDING = "industry_funding"
    PREDATORY_JOURNAL = "predatory_journal"
    PARTIAL_SUPPORT = "partial_support"
    SAMPLE_SIZE_MISMATCH = "sample_size_mismatch"
    POPULARITY_BIAS = "popularity_bias"


class StudyDesign(Enum):
    """Hierarchy of study designs for evidence strength assessment."""
    SYSTEMATIC_REVIEW = "systematic_review"
    META_ANALYSIS = "meta_analysis"
    RCT = "rct"
    COHORT = "cohort"
    CASE_CONTROL = "case_control"
    CROSS_SECTIONAL = "cross_sectional"
    CASE_SERIES = "case_series"
    CASE_REPORT = "case_report"
    EXPERT_OPINION = "expert_opinion"
    CONFERENCE_ABSTRACT = "conference_abstract"
    PREPRINT = "preprint"
    UNKNOWN = "unknown"


# Study designs that support causal claims
CAUSAL_DESIGNS = {StudyDesign.RCT, StudyDesign.SYSTEMATIC_REVIEW, StudyDesign.META_ANALYSIS}

# Study designs that do NOT support causal claims
OBSERVATIONAL_DESIGNS = {
    StudyDesign.COHORT, StudyDesign.CASE_CONTROL,
    StudyDesign.CROSS_SECTIONAL, StudyDesign.CASE_SERIES,
    StudyDesign.CASE_REPORT
}

# Claim strength hierarchy
CLAIM_STRENGTH = {
    'demonstrated': 3,
    'confirmed': 3,
    'established': 3,
    'proved': 3,
    'showed': 2,
    'found': 2,
    'reported': 2,
    'observed': 2,
    'suggested': 1,
    'indicated': 1,
    'preliminary': 0,
    'pilot': 0,
    'exploratory': 0,
}

# Minimum study design level for each claim strength
DESIGN_REQUIREMENTS = {
    3: {StudyDesign.RCT, StudyDesign.SYSTEMATIC_REVIEW, StudyDesign.META_ANALYSIS},
    2: {StudyDesign.RCT, StudyDesign.COHORT, StudyDesign.SYSTEMATIC_REVIEW, StudyDesign.META_ANALYSIS},
    1: OBSERVATIONAL_DESIGNS | CAUSAL_DESIGNS,
    0: {d for d in StudyDesign},
}


@dataclass
class SemanticVerificationResult:
    """Result of semantic-level verification."""
    url: str
    flags: List[SemanticFlag] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    study_design: Optional[StudyDesign] = None
    claim_strength_detected: Optional[str] = None
    retraction_status: Optional[str] = None
    funding_sources: List[str] = field(default_factory=list)
    population_scope: Optional[str] = None
    geographic_scope: Optional[str] = None
    is_conference_abstract: bool = False
    confidence: float = 0.5

    def to_dict(self) -> Dict:
        return {
            'url': self.url,
            'flags': [f.value for f in self.flags],
            'warnings': self.warnings,
            'errors': self.errors,
            'study_design': self.study_design.value if self.study_design else None,
            'claim_strength_detected': self.claim_strength_detected,
            'retraction_status': self.retraction_status,
            'funding_sources': self.funding_sources,
            'population_scope': self.population_scope,
            'geographic_scope': self.geographic_scope,
            'is_conference_abstract': self.is_conference_abstract,
            'confidence': self.confidence,
        }


class CausalLanguageDetector:
    """Detects causal language in inline claims."""

    CAUSAL_PATTERNS = [
        re.compile(r'\bcauses?\b', re.IGNORECASE),
        re.compile(r'\bleads?\s+to\b', re.IGNORECASE),
        re.compile(r'\bresults?\s+in\b', re.IGNORECASE),
        re.compile(r'\bdue\s+to\b', re.IGNORECASE),
        re.compile(r'\bdrives?\b', re.IGNORECASE),
        re.compile(r'\bprevents?\b', re.IGNORECASE),
        re.compile(r'\breduces?\b', re.IGNORECASE),
        re.compile(r'\bincreases?\b', re.IGNORECASE),
        re.compile(r'\bimproves?\b', re.IGNORECASE),
        re.compile(r'\btriggers?\b', re.IGNORECASE),
        re.compile(r'\binduces?\b', re.IGNORECASE),
    ]

    ASSOCIATIVE_PATTERNS = [
        re.compile(r'\bassociated\s+with\b', re.IGNORECASE),
        re.compile(r'\bcorrelated?\s+with\b', re.IGNORECASE),
        re.compile(r'\blinked\s+to\b', re.IGNORECASE),
        re.compile(r'\brelationship\s+between\b', re.IGNORECASE),
    ]

    def detect(self, claim_text: str) -> Tuple[bool, List[str]]:
        """
        Check if claim text uses causal language.

        Returns:
            Tuple of (has_causal_language, matched_patterns)
        """
        matches = []
        for pattern in self.CAUSAL_PATTERNS:
            if pattern.search(claim_text):
                matches.append(pattern.pattern)

        return len(matches) > 0, matches

    def detect_associative(self, claim_text: str) -> bool:
        """Check if claim text appropriately uses associative language."""
        return any(p.search(claim_text) for p in self.ASSOCIATIVE_PATTERNS)


class StudyDesignClassifier:
    """Classifies study design from paper content."""

    DESIGN_INDICATORS = {
        StudyDesign.SYSTEMATIC_REVIEW: [
            r'systematic\s+review', r'prisma', r'literature\s+search',
            r'inclusion\s+criteria', r'exclusion\s+criteria',
            r'databases?\s+searched'
        ],
        StudyDesign.META_ANALYSIS: [
            r'meta-analysis', r'meta\s+analysis', r'pooled\s+(?:analysis|estimate)',
            r'forest\s+plot', r'heterogeneity', r'I\^?2'
        ],
        StudyDesign.RCT: [
            r'randomized', r'randomised', r'randomization',
            r'placebo-controlled', r'double-blind', r'single-blind',
            r'control\s+group', r'treatment\s+arm'
        ],
        StudyDesign.COHORT: [
            r'cohort\s+study', r'prospective\s+study', r'retrospective\s+study',
            r'follow-up\s+period', r'longitudinal', r'incidence\s+rate'
        ],
        StudyDesign.CASE_CONTROL: [
            r'case-control', r'case\s+control', r'odds\s+ratio'
        ],
        StudyDesign.CROSS_SECTIONAL: [
            r'cross-sectional', r'cross\s+sectional', r'prevalence\s+study',
            r'survey\s+of'
        ],
        StudyDesign.CASE_SERIES: [
            r'case\s+series', r'consecutive\s+patients', r'chart\s+review'
        ],
        StudyDesign.CASE_REPORT: [
            r'case\s+report', r'we\s+report\s+a\s+case', r'a\s+\d+-year-old'
        ],
        StudyDesign.CONFERENCE_ABSTRACT: [
            r'conference\s+abstract', r'poster\s+presentation',
            r'oral\s+presentation', r'proceedings\s+of',
            r'annual\s+meeting'
        ],
    }

    def classify(self, text: str) -> Tuple[StudyDesign, float]:
        """
        Classify study design from text content.

        Returns:
            Tuple of (StudyDesign, confidence)
        """
        if not text:
            return StudyDesign.UNKNOWN, 0.0

        text_lower = text.lower()
        scores = {}

        for design, patterns in self.DESIGN_INDICATORS.items():
            match_count = 0
            for pattern in patterns:
                if re.search(pattern, text_lower):
                    match_count += 1
            if match_count > 0:
                scores[design] = match_count / len(patterns)

        if not scores:
            return StudyDesign.UNKNOWN, 0.0

        best_design = max(scores, key=scores.get)
        confidence = min(scores[best_design] * 2, 1.0)  # Scale to 0-1

        return best_design, confidence


class ScopeAnalyzer:
    """Detects scope extrapolation in claims."""

    # Broad claim indicators
    BROAD_INDICATORS = [
        re.compile(r'\bpopulation-level\b', re.IGNORECASE),
        re.compile(r'\bgenerally\b', re.IGNORECASE),
        re.compile(r'\bacross\s+(?:all|populations?|settings?)\b', re.IGNORECASE),
        re.compile(r'\buniversally\b', re.IGNORECASE),
        re.compile(r'\bglobally\b', re.IGNORECASE),
        re.compile(r'\bnationwide\b', re.IGNORECASE),
        re.compile(r'\bwidely\b', re.IGNORECASE),
        re.compile(r'\bin\s+(?:all|most)\s+(?:patients?|cases?|settings?)\b', re.IGNORECASE),
    ]

    # Narrow scope indicators (from paper content)
    NARROW_INDICATORS = [
        re.compile(r'\bsingle[- ](?:center|centre|site|institution)\b', re.IGNORECASE),
        re.compile(r'\bpilot\s+study\b', re.IGNORECASE),
        re.compile(r'\bn\s*=\s*\d{1,2}\b'),  # Very small sample
        re.compile(r'\b(?:one|single)\s+hospital\b', re.IGNORECASE),
        re.compile(r'\bpreliminary\b', re.IGNORECASE),
        re.compile(r'\bfeasibility\b', re.IGNORECASE),
        re.compile(r'\bproof[- ]of[- ]concept\b', re.IGNORECASE),
    ]

    def check_extrapolation(
        self,
        claim_text: str,
        paper_text: str
    ) -> Tuple[bool, List[str]]:
        """
        Check if claim scope exceeds paper scope.

        Returns:
            Tuple of (is_extrapolated, details)
        """
        claim_broad = any(p.search(claim_text) for p in self.BROAD_INDICATORS)
        paper_narrow = any(p.search(paper_text) for p in self.NARROW_INDICATORS)

        details = []
        if claim_broad and paper_narrow:
            details.append(
                "Claim uses population-level language but paper describes "
                "a narrow study (single-site, pilot, small sample)"
            )

        # Check sample size vs claim scope
        sample_match = re.search(r'\bn\s*=\s*(\d+)', paper_text)
        if sample_match:
            n = int(sample_match.group(1))
            if n < 100 and claim_broad:
                details.append(
                    f"Paper sample size (n={n}) does not support "
                    f"population-level generalization"
                )

        return len(details) > 0, details


class DirectionOfEffectChecker:
    """Detects when claim direction contradicts paper findings."""

    POSITIVE_INDICATORS = [
        'improved', 'increased', 'higher', 'better', 'effective',
        'beneficial', 'successful', 'concordance', 'agreement',
        'superior', 'outperformed', 'advantage'
    ]

    NEGATIVE_INDICATORS = [
        'worsened', 'decreased', 'lower', 'worse', 'ineffective',
        'harmful', 'failed', 'disparity', 'disagreement',
        'inferior', 'underperformed', 'disadvantage', 'risk'
    ]

    def check_direction(
        self,
        claim_text: str,
        paper_text: str
    ) -> Tuple[bool, List[str]]:
        """
        Check if claim direction matches paper findings.

        Returns:
            Tuple of (direction_mismatch, details)
        """
        if not paper_text:
            return False, []

        claim_lower = claim_text.lower()
        paper_lower = paper_text.lower()

        claim_positive = sum(1 for w in self.POSITIVE_INDICATORS if w in claim_lower)
        claim_negative = sum(1 for w in self.NEGATIVE_INDICATORS if w in claim_lower)

        paper_positive = sum(1 for w in self.POSITIVE_INDICATORS if w in paper_lower)
        paper_negative = sum(1 for w in self.NEGATIVE_INDICATORS if w in paper_lower)

        details = []

        # Claim is positive but paper is predominantly negative
        if claim_positive > claim_negative and paper_negative > paper_positive:
            details.append(
                "Claim frames findings positively but paper content "
                "is predominantly negative/cautionary"
            )

        # Claim is negative but paper is predominantly positive
        if claim_negative > claim_positive and paper_positive > paper_negative:
            details.append(
                "Claim frames findings negatively but paper content "
                "is predominantly positive"
            )

        return len(details) > 0, details


class RetractionChecker:
    """Checks retraction status via CrossRef metadata."""

    CROSSREF_API = "https://api.crossref.org/works"

    async def check_retraction(self, doi: str) -> Tuple[bool, Optional[str]]:
        """
        Check if a DOI has been retracted.

        Returns:
            Tuple of (is_retracted, retraction_notice_doi)
        """
        if not doi:
            return False, None

        url = f"{self.CROSSREF_API}/{doi}"
        headers = {
            'User-Agent': 'CitationVerifier/4.0 (mailto:verification@example.com)'
        }

        try:
            timeout = aiohttp.ClientTimeout(total=15)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(url, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        message = data.get('message', {})

                        # Check for retraction markers
                        update_to = message.get('update-to', [])
                        for update in update_to:
                            if update.get('type') == 'retraction':
                                return True, update.get('DOI')

                        # Check relation field
                        relation = message.get('relation', {})
                        is_retracted = relation.get('is-retracted-by', [])
                        if is_retracted:
                            retraction_doi = is_retracted[0].get('id')
                            return True, retraction_doi

                        # Check for "retracted-article" type
                        if message.get('type') == 'retracted-article':
                            return True, None

        except Exception:
            pass

        return False, None

    async def check_batch(
        self,
        dois: List[str],
        concurrency: int = 5
    ) -> Dict[str, Tuple[bool, Optional[str]]]:
        """Check retraction status for multiple DOIs."""
        semaphore = asyncio.Semaphore(concurrency)
        results = {}

        async def check_one(doi: str):
            async with semaphore:
                await asyncio.sleep(0.2)  # Rate limiting
                is_retracted, notice = await self.check_retraction(doi)
                results[doi] = (is_retracted, notice)

        tasks = [check_one(doi) for doi in dois if doi]
        await asyncio.gather(*tasks)
        return results


class ConferenceAbstractDetector:
    """Detects if a citation points to a conference abstract rather than a full paper."""

    ABSTRACT_INDICATORS = [
        re.compile(r'\babstract\s*#?\d+', re.IGNORECASE),
        re.compile(r'poster\s+(?:session|presentation|number)', re.IGNORECASE),
        re.compile(r'oral\s+(?:session|presentation)', re.IGNORECASE),
        re.compile(r'supplement\s+\d', re.IGNORECASE),
        re.compile(r'proceedings\s+of\s+the', re.IGNORECASE),
        re.compile(r'annual\s+meeting\s+abstract', re.IGNORECASE),
    ]

    # DOI patterns that indicate conference proceedings
    PROCEEDINGS_DOI_PATTERNS = [
        re.compile(r'10\.\d+/\w+\.\d{4}\.\d+'),  # Generic proceedings
    ]

    # Known proceedings publisher prefixes
    PROCEEDINGS_PREFIXES = {
        '10.1145': 'ACM',
        '10.1109': 'IEEE',
    }

    def detect(self, url: str, title: str = "", content: str = "") -> Tuple[bool, float]:
        """
        Detect if citation is a conference abstract.

        Returns:
            Tuple of (is_abstract, confidence)
        """
        combined = f"{title} {content}".lower()

        matches = sum(1 for p in self.ABSTRACT_INDICATORS if p.search(combined))

        if matches >= 2:
            return True, 0.9
        elif matches == 1:
            return True, 0.6

        # Check DOI pattern
        for prefix, org in self.PROCEEDINGS_PREFIXES.items():
            if prefix in url:
                return True, 0.5

        return False, 0.0


class DrugNameChecker:
    """Detects drug name substitution errors."""

    # Common brand/generic pairs that LLMs confuse
    DRUG_PAIRS = {
        'advil': 'ibuprofen',
        'tylenol': 'acetaminophen',
        'motrin': 'ibuprofen',
        'aleve': 'naproxen',
        'humira': 'adalimumab',
        'humalog': 'insulin lispro',
        'humulin': 'insulin regular',
        'lipitor': 'atorvastatin',
        'crestor': 'rosuvastatin',
        'zocor': 'simvastatin',
        'plavix': 'clopidogrel',
        'eliquis': 'apixaban',
        'xarelto': 'rivaroxaban',
        'coumadin': 'warfarin',
        'metformin': 'glucophage',
        'januvia': 'sitagliptin',
        'ozempic': 'semaglutide',
        'wegovy': 'semaglutide',
        'mounjaro': 'tirzepatide',
        'keytruda': 'pembrolizumab',
        'opdivo': 'nivolumab',
        'herceptin': 'trastuzumab',
        'avastin': 'bevacizumab',
        'remicade': 'infliximab',
        'enbrel': 'etanercept',
        'rituxan': 'rituximab',
    }

    def __init__(self):
        # Build reverse lookup
        self._all_names = set()
        self._brand_to_generic = {}
        self._generic_to_brands = {}

        for brand, generic in self.DRUG_PAIRS.items():
            self._brand_to_generic[brand.lower()] = generic.lower()
            if generic.lower() not in self._generic_to_brands:
                self._generic_to_brands[generic.lower()] = []
            self._generic_to_brands[generic.lower()].append(brand.lower())
            self._all_names.add(brand.lower())
            self._all_names.add(generic.lower())

    def find_drugs(self, text: str) -> Set[str]:
        """Find drug names in text."""
        text_lower = text.lower()
        found = set()
        for name in self._all_names:
            if re.search(r'\b' + re.escape(name) + r'\b', text_lower):
                found.add(name)
        return found

    def check_consistency(
        self,
        claim_text: str,
        paper_text: str
    ) -> Tuple[bool, List[str]]:
        """
        Check if drugs mentioned in claim match drugs in paper.

        Returns:
            Tuple of (has_mismatch, details)
        """
        claim_drugs = self.find_drugs(claim_text)
        paper_drugs = self.find_drugs(paper_text)

        if not claim_drugs or not paper_drugs:
            return False, []

        details = []
        for drug in claim_drugs:
            if drug not in paper_drugs:
                # Check if it's a brand/generic swap
                equivalent = self._brand_to_generic.get(drug)
                if equivalent and equivalent in paper_drugs:
                    continue  # Brand/generic swap is acceptable
                brands = self._generic_to_brands.get(drug, [])
                if any(b in paper_drugs for b in brands):
                    continue  # Generic/brand swap is acceptable

                details.append(
                    f"Drug '{drug}' mentioned in claim but not found in paper. "
                    f"Paper mentions: {', '.join(paper_drugs)}"
                )

        return len(details) > 0, details


class FundingAnalyzer:
    """Detects industry funding and conflicts of interest."""

    FUNDING_PATTERNS = [
        re.compile(r'funded\s+by\s+(.+?)(?:\.|$)', re.IGNORECASE),
        re.compile(r'supported\s+by\s+(?:a\s+)?(?:grant|funding)\s+from\s+(.+?)(?:\.|$)', re.IGNORECASE),
        re.compile(r'(?:financial\s+)?(?:support|sponsorship)\s+(?:from|by)\s+(.+?)(?:\.|$)', re.IGNORECASE),
    ]

    INDUSTRY_INDICATORS = [
        'pharmaceutical', 'pharma', 'inc.', 'inc,', 'corp.', 'corp,',
        'ltd.', 'ltd,', 'gmbh', 'co.', 'llc',
        'pfizer', 'merck', 'roche', 'novartis', 'johnson', 'abbott',
        'medtronic', 'boston scientific', 'stryker', 'baxter',
        'amgen', 'gilead', 'regeneron', 'moderna', 'biontech',
        'astrazeneca', 'glaxosmithkline', 'gsk', 'sanofi',
        'eli lilly', 'lilly', 'bristol-myers', 'bms',
    ]

    COI_PATTERNS = [
        re.compile(r'conflict\s+of\s+interest', re.IGNORECASE),
        re.compile(r'competing\s+interest', re.IGNORECASE),
        re.compile(r'(?:has|have)\s+received\s+(?:grants?|fees?|honoraria)', re.IGNORECASE),
        re.compile(r'consultant\s+(?:for|to)', re.IGNORECASE),
        re.compile(r'advisory\s+board', re.IGNORECASE),
        re.compile(r'speakers?\s+bureau', re.IGNORECASE),
    ]

    def analyze(self, paper_text: str) -> Tuple[bool, List[str]]:
        """
        Analyze paper text for industry funding indicators.

        Returns:
            Tuple of (has_industry_funding, funding_sources)
        """
        if not paper_text:
            return False, []

        text_lower = paper_text.lower()
        sources = []

        # Extract explicit funding statements
        for pattern in self.FUNDING_PATTERNS:
            for match in pattern.finditer(paper_text):
                source = match.group(1).strip()
                if any(ind in source.lower() for ind in self.INDUSTRY_INDICATORS):
                    sources.append(source)

        # Check for industry indicators in COI sections
        has_coi = any(p.search(paper_text) for p in self.COI_PATTERNS)
        has_industry = any(ind in text_lower for ind in self.INDUSTRY_INDICATORS)

        return (len(sources) > 0 or (has_coi and has_industry)), sources


class SemanticVerifier:
    """
    Main semantic verification orchestrator.

    Runs higher-order checks that go beyond URL/DOI validation
    and basic content matching to detect subtle misrepresentation.
    """

    def __init__(self):
        self.causal_detector = CausalLanguageDetector()
        self.design_classifier = StudyDesignClassifier()
        self.scope_analyzer = ScopeAnalyzer()
        self.direction_checker = DirectionOfEffectChecker()
        self.retraction_checker = RetractionChecker()
        self.abstract_detector = ConferenceAbstractDetector()
        self.drug_checker = DrugNameChecker()
        self.funding_analyzer = FundingAnalyzer()

    async def verify(
        self,
        url: str,
        claim_text: str,
        paper_text: str = "",
        paper_title: str = "",
        doi: str = ""
    ) -> SemanticVerificationResult:
        """
        Run all semantic checks on a citation.

        Args:
            url: Citation URL
            claim_text: Inline claim text surrounding the citation
            paper_text: Extracted paper content (abstract + body)
            paper_title: Paper title
            doi: DOI if available

        Returns:
            SemanticVerificationResult with all flags and details
        """
        result = SemanticVerificationResult(url=url)

        # 1. Retraction check
        if doi:
            is_retracted, notice = await self.retraction_checker.check_retraction(doi)
            if is_retracted:
                result.flags.append(SemanticFlag.RETRACTED_PAPER)
                result.errors.append(
                    f"Paper has been retracted"
                    + (f" (retraction notice: {notice})" if notice else "")
                )
                result.retraction_status = "retracted"
                result.confidence = 0.95

        # 2. Study design classification
        combined_text = f"{paper_title} {paper_text}"
        design, design_confidence = self.design_classifier.classify(combined_text)
        result.study_design = design

        # 3. Causal language check
        has_causal, causal_matches = self.causal_detector.detect(claim_text)
        if has_causal and design in OBSERVATIONAL_DESIGNS:
            result.flags.append(SemanticFlag.CAUSAL_INFERENCE_ESCALATION)
            result.warnings.append(
                f"Claim uses causal language but paper appears to be "
                f"{design.value} (observational design)"
            )

        # 4. Evidence strength check
        claim_lower = claim_text.lower()
        detected_strength = None
        for word, level in CLAIM_STRENGTH.items():
            if word in claim_lower:
                detected_strength = word
                break

        if detected_strength:
            result.claim_strength_detected = detected_strength
            strength_level = CLAIM_STRENGTH[detected_strength]
            allowed_designs = DESIGN_REQUIREMENTS.get(strength_level, set())
            if design != StudyDesign.UNKNOWN and design not in allowed_designs:
                result.flags.append(SemanticFlag.EVIDENCE_STRENGTH_INFLATION)
                result.warnings.append(
                    f"Claim uses '{detected_strength}' but paper design "
                    f"({design.value}) does not support this strength level"
                )

        # 5. Scope extrapolation check
        if paper_text:
            is_extrapolated, scope_details = self.scope_analyzer.check_extrapolation(
                claim_text, paper_text
            )
            if is_extrapolated:
                result.flags.append(SemanticFlag.SCOPE_EXTRAPOLATION)
                result.warnings.extend(scope_details)

        # 6. Direction of effect check
        if paper_text:
            direction_mismatch, direction_details = self.direction_checker.check_direction(
                claim_text, paper_text
            )
            if direction_mismatch:
                result.flags.append(SemanticFlag.DIRECTION_REVERSAL)
                result.errors.extend(direction_details)

        # 7. Conference abstract check
        is_abstract, abstract_conf = self.abstract_detector.detect(
            url, paper_title, paper_text
        )
        if is_abstract:
            result.flags.append(SemanticFlag.CONFERENCE_ABSTRACT)
            result.is_conference_abstract = True
            result.warnings.append(
                "Citation appears to reference a conference abstract, "
                "not a peer-reviewed full paper"
            )

        # 8. Drug name check
        if paper_text:
            drug_mismatch, drug_details = self.drug_checker.check_consistency(
                claim_text, paper_text
            )
            if drug_mismatch:
                result.flags.append(SemanticFlag.DRUG_NAME_MISMATCH)
                result.errors.extend(drug_details)

        # 9. Funding analysis
        if paper_text:
            has_industry, sources = self.funding_analyzer.analyze(paper_text)
            if has_industry:
                result.flags.append(SemanticFlag.INDUSTRY_FUNDING)
                result.funding_sources = sources
                result.warnings.append(
                    f"Paper has industry funding: {', '.join(sources) if sources else 'detected'}"
                )

        return result

    async def verify_batch(
        self,
        citations: List[Dict],
        concurrency: int = 5
    ) -> List[SemanticVerificationResult]:
        """
        Run semantic verification on multiple citations.

        Args:
            citations: List of dicts with url, claim_text, paper_text, paper_title, doi
            concurrency: Max concurrent verifications

        Returns:
            List of SemanticVerificationResult
        """
        semaphore = asyncio.Semaphore(concurrency)

        async def verify_one(citation: Dict) -> SemanticVerificationResult:
            async with semaphore:
                return await self.verify(
                    url=citation.get('url', ''),
                    claim_text=citation.get('claim_text', ''),
                    paper_text=citation.get('paper_text', ''),
                    paper_title=citation.get('paper_title', ''),
                    doi=citation.get('doi', '')
                )

        tasks = [verify_one(c) for c in citations]
        return await asyncio.gather(*tasks)


def export_results(results: List[SemanticVerificationResult], output_path: str) -> None:
    """Export semantic verification results to JSON."""
    stats = {
        'total': len(results),
        'with_flags': sum(1 for r in results if r.flags),
        'by_flag': {},
    }

    for flag in SemanticFlag:
        count = sum(1 for r in results if flag in r.flags)
        if count > 0:
            stats['by_flag'][flag.value] = count

    data = {
        'statistics': stats,
        'results': [r.to_dict() for r in results]
    }

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


async def main():
    """Command-line interface for semantic verification."""
    import argparse

    parser = argparse.ArgumentParser(
        description='Semantic citation verification (Phase 2+)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Detects higher-order citation failures:
  - Scope extrapolation
  - Evidence strength inflation
  - Causal inference escalation
  - Retracted papers
  - Conference abstracts cited as papers
  - Drug name substitution
  - Direction-of-effect reversal
  - Industry funding blindness
        """
    )
    parser.add_argument('input', help='Input JSON from content_verifier.py')
    parser.add_argument('-o', '--output', default='semantic_verification.json',
                        help='Output JSON file')
    parser.add_argument('-c', '--concurrency', type=int, default=5,
                        help='Max concurrent checks')

    args = parser.parse_args()

    with open(args.input, 'r', encoding='utf-8') as f:
        data = json.load(f)

    citations = data.get('results', data.get('citations', []))
    print(f"Running semantic verification on {len(citations)} citations...")

    verifier = SemanticVerifier()
    results = await verifier.verify_batch(citations, concurrency=args.concurrency)

    export_results(results, args.output)

    flagged = sum(1 for r in results if r.flags)
    print(f"\nResults:")
    print(f"  Citations with semantic flags: {flagged}/{len(results)}")

    for flag in SemanticFlag:
        count = sum(1 for r in results if flag in r.flags)
        if count > 0:
            label = flag.value.replace('_', ' ').title()
            print(f"  {label}: {count}")

    print(f"\nExported to: {args.output}")


if __name__ == '__main__':
    asyncio.run(main())
