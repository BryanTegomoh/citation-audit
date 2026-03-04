# Citation 9 Verification Report

**Citation under review:**
Gerber JS, Prasad PA, Fiks AG, et al. Effect of an Outpatient Antimicrobial Stewardship Intervention on Broad-Spectrum Antibiotic Prescribing by Primary Care Pediatricians: A Randomized Trial. *JAMA*. 2013;309(22):2345-52. doi:10.1001/jama.2013.6287.

**Audit context:** OpenEvidence response on antibiotic stewardship strategies in outpatient respiratory infections
**Date verified:** March 4, 2026

---

## 1. Paper Existence and PMID Verification

**PMID 23757082: CONFIRMED.**

The paper exists at [PubMed](https://pubmed.ncbi.nlm.nih.gov/23757082/) and at [JAMA Network](https://jamanetwork.com/journals/jama/fullarticle/1696098). The DOI (10.1001/jama.2013.6287) resolves via CrossRef to the correct JAMA article page. The DOI prefix 10.1001 correctly corresponds to the JAMA/AMA publisher.

---

## 2. Main Findings (from Abstract and PubMed Record)

**Primary outcome:** Broad-spectrum antibiotic prescribing for acute respiratory tract infections (ARTIs) in pediatric primary care.

**Key results:**

| Group | Baseline Broad-Spectrum Rate | Post-Intervention Rate | Absolute Reduction |
|-------|------------------------------|------------------------|--------------------|
| Intervention (9 practices) | 26.8% | 14.3% | 12.5 percentage points |
| Control (9 practices) | 28.4% | 22.6% | 5.8 percentage points |

**Difference-in-differences:** 6.7 percentage points (P = .01 for differences in trajectories).

**Secondary finding:** The intervention improved adherence to prescribing guidelines for common bacterial ARTIs. It did not affect antibiotic prescribing for viral infections (where prescribing was already low and not the target).

**For pneumonia specifically:** Off-guideline prescribing fell from 15.7% to 4.2% in intervention sites versus 17.1% to 16.3% in controls.

---

## 3. Intervention Description

**Intervention components:**
1. One 1-hour on-site clinician education session (June 2010)
2. One year of personalized, quarterly audit and feedback of prescribing patterns for bacterial and viral ARTIs

**Control:** Usual practice.

**Duration:** 32-month study period (enrollment June 2010, intervention period through approximately June 2011, with continued monitoring).

---

## 4. Setting

**CONFIRMED: Pediatric primary care.**

- Network of 25 pediatric primary care practices in Pennsylvania and New Jersey
- 18 practices (162 clinicians) participated in the randomized trial
- All practices used a common electronic health record (EHR) system
- Affiliated with The Children's Hospital of Philadelphia (CHOP)
- Cluster randomized design (randomization at the practice level, not individual clinician level)

---

## 5. Broad-Spectrum Prescribing Specificity

**CONFIRMED: The study is specifically about broad-spectrum antibiotic prescribing, not total prescribing.**

The primary outcome was the proportion of antibiotic prescriptions for bacterial ARTIs that were broad-spectrum (e.g., amoxicillin-clavulanate, fluoroquinolones, cephalosporins) rather than narrow-spectrum first-line agents (e.g., amoxicillin). The intervention aimed to shift prescribing from broad-spectrum to narrow-spectrum agents for conditions where narrow-spectrum antibiotics are guideline-recommended, not to reduce overall antibiotic use.

This is a critical distinction. The study did not aim to reduce antibiotic prescribing for bacterial infections overall. It aimed to improve the choice of antibiotic (narrow over broad) for infections that appropriately warranted antibiotic treatment.

---

## 6. Inline Claim Analysis

**No specific inline claim cites [9] in the OpenEvidence response.**

Based on the existing audit report (which documents Citation 9 under Phase 2 as "N/A: appears in figures section with no specific inline claim"), and confirmed by WebFetch of the OpenEvidence page (where citations [8] and [9] were not located in the main body text, appearing only in a figures/references section that may not render fully in automated fetches):

- Citations [1] through [7] appear inline in the response body supporting specific claims
- Citation [8] (Stenehjem et al.) has inline claims (the "48% to 26%" figure)
- Citation [9] (Gerber et al.) has NO inline claim associated with it

The OpenEvidence response does not make any specific statement of the form "Broad-spectrum prescribing decreased by X% [9]" or attribute any finding to the Gerber study within its prose.

---

## 7. Decoration Citation Assessment

**Yes, this is a decoration citation.**

Citation [9] exhibits the hallmarks of a decoration citation:

1. **No inline claim:** The citation is not used to support any specific assertion in the response text.
2. **Appears only in supplementary section:** It is listed in the figures/references area, not woven into the argument.
3. **Topically relevant but functionally orphaned:** The paper is highly relevant to outpatient antibiotic stewardship (the response's topic), making its inclusion look appropriate at a glance. But it does no actual evidentiary work in the response.
4. **Reference list padding:** Including a landmark JAMA RCT in the reference list increases the apparent rigor and comprehensiveness of the response without the citation supporting any specific claim.

**Why this matters:** Decoration citations create the appearance of thorough sourcing without the substance. A physician reviewing the reference list would see "JAMA, 2013, randomized trial" and reasonably assume the response draws on its findings. It does not. The citation exists to signal rigor, not to provide evidence.

**Classification:** DECORATION_CITATION (included in reference list to signal comprehensiveness without supporting any specific inline claim).

**Severity:** Low (no incorrect claim is made; the paper is real and topically relevant). However, decoration citations are a recognized pattern in LLM-generated medical content that inflates perceived evidence quality. The pattern becomes concerning at scale: if 1-2 of 9 citations are decorative, the response appears more thoroughly sourced than it actually is.

---

## 8. Metadata Verification

| Field | Claimed | Verified | Status |
|-------|---------|----------|--------|
| First author | Gerber JS | Jeffrey S. Gerber | CORRECT |
| Co-authors | Prasad PA, Fiks AG, et al. | Prasad PA, Fiks AG, Localio AR, Grundmeier RW, Bell LM, Wasserman RC, Keren R, Zaoutis TE | CORRECT (et al. appropriately used for 9 authors) |
| Journal | JAMA | JAMA (Journal of the American Medical Association) | CORRECT |
| Year | 2013 | 2013 (June 12) | CORRECT |
| Volume | 309 | 309 | CORRECT |
| Issue | 22 | 22 | CORRECT |
| Pages | 2345-52 | 2345-2352 | CORRECT (abbreviated form is standard) |
| DOI | 10.1001/jama.2013.6287 | 10.1001/jama.2013.6287 | CORRECT |
| PMID | 23757082 | 23757082 | CORRECT |
| DOI prefix | 10.1001 | JAMA/AMA publisher prefix | CORRECT |

**All metadata verified. No errors detected.**

---

## Summary Verdict

| Phase | Result |
|-------|--------|
| Phase 0 (DOI exists) | PASS: DOI exists in CrossRef, resolves correctly |
| Phase 1 (URL resolves) | PASS: PubMed, JAMA Network both accessible |
| Phase 2 (claim supported) | N/A: No inline claim to verify |
| Phase 3 (metadata correct) | PASS: All fields verified against PubMed and CrossRef |
| Phase 4 (correction) | N/A |

**Overall: CLEAN citation with DECORATION_CITATION classification.**

The paper is real, the metadata is accurate, and it is a landmark study in pediatric outpatient antibiotic stewardship. However, the OpenEvidence response does not cite any specific finding from this paper. It serves as reference list padding rather than evidentiary support for a claim.

---

## Sources Consulted

- [PubMed Record (PMID 23757082)](https://pubmed.ncbi.nlm.nih.gov/23757082/)
- [JAMA Full Article](https://jamanetwork.com/journals/jama/fullarticle/1696098)
- [CrossRef API (DOI 10.1001/jama.2013.6287)](https://api.crossref.org/works/10.1001/jama.2013.6287)
- [ResearchGate Record](https://www.researchgate.net/publication/237147624)

---

*Verification conducted March 4, 2026 using the Five-Phase Citation Verification Pipeline.*
