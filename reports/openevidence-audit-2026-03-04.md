# OpenEvidence Citation Accuracy Audit

**Date:** March 4, 2026
**Methodology:** Five-Phase Citation Verification Pipeline v3.3
**Target:** OpenEvidence response on antibiotic stewardship strategies in outpatient respiratory infections
**Source:** [OpenEvidence query](https://www.openevidence.com/ask/d252c9f9-08ed-4db8-b6ab-8f0fd13ce058)
**Auditor:** Bryan Tegomoh, MD, MPH

---

## Summary

| Metric | Result |
|--------|--------|
| Citations analyzed | 9 |
| Phase 0-1 pass (DOI exists, URL resolves) | 9/9 (100%) |
| Phase 2-3 pass (claims supported, metadata correct) | 5/9 (56%) |
| Citations with claim-citation alignment failures | 4/9 (44%) |
| Fabricated papers | 0 |
| Fabricated DOIs | 0 |
| Misattributed statistics | 2 |
| Statistic conflation (misleading presentation) | 1 |
| Intervention mischaracterization | 1 |
| Unverified statistic (possible fabrication) | 1 ("85% decrease") |

**Bottom line:** Every citation points to a real paper with accurate metadata. A standard link-check audit would return a perfect score. Content-level verification reveals that 44% of citations have claim-citation alignment problems, ranging from misattributed statistics to misleading data presentation. These are the errors that reach clinicians.

---

## Why This Matters for OpenEvidence

OpenEvidence's value proposition is sourced, grounded citations that physicians can trust. The platform processes over 100 million clinical consultations. When a physician reads "prescribing dropped from 48% to 26%" with a JAMA Network Open citation attached, they trust that number. They may adjust their practice expectations based on it.

The actual intervention result was 48% to 33%. The 26% figure comes from a separate sustainability analysis one to two years later. Presenting these as a single effect nearly doubles the apparent magnitude of the immediate intervention.

This category of error (content-level misalignment) is invisible to URL checking, DOI validation, and metadata verification. It requires reading the cited paper and comparing its findings to the inline claim. That is the gap this audit addresses.

---

## Methodology Applied

Each citation was verified through all five phases of the Citation Verification Pipeline:

| Phase | What It Checks | How |
|-------|---------------|-----|
| Phase 0 | DOI exists in CrossRef registry | CrossRef API query |
| Phase 1 | URL resolves to accessible resource | HTTP status check |
| Phase 2 | Paper supports the specific inline claim | Content comparison against source |
| Phase 3 | Author, year, journal, DOI metadata are correct | Metadata cross-reference |
| Phase 4 | Correction identification | Source tracing for misattributed claims |

Phase 2 is where standard verification stops and this methodology begins. Only 21% of citation errors in LLM-generated content are HTTP-detectable (broken links, failed DOIs). The remaining 79% require content-level verification.

---

## Citation-by-Citation Results

### Citation 1: Sur & Plesa, American Family Physician, 2022

> Sur DKC, Plesa ML. Antibiotic Use in Acute Upper Respiratory Tract Infections. *American Family Physician*. 2022;106(6):628-636.

| Phase | Result |
|-------|--------|
| Phase 0 | N/A (AFP does not assign DOIs, standard for this journal) |
| Phase 1 | Paper confirmed at PubMed (PMID 36521460) and AAFP website |
| Phase 2 | All verifiable claims supported |
| Phase 3 | Authors, journal, year, volume, pages: all correct |

**Claims verified against source:**

- CDC identifies nonspecific URIs, viral pharyngitis, uncomplicated acute bacterial rhinosinusitis, and acute otitis media as high-priority targets: **Confirmed**
- GAS pharyngitis treatment with amoxicillin/penicillin V as first-line: **Confirmed** ("A 10-day course of penicillin V or amoxicillin is the first-line therapy")
- Delayed prescribing reduces antibiotic use but decreases patient satisfaction: **Confirmed**
- PEN-FAST tool described as "a validated, point-of-care clinical decision rule": **Confirmed**
- Less than 1% of patients reporting penicillin allergy have confirmed allergy: **Confirmed** (paper states: "less than 1% of the population has a confirmed penicillin allergy")
- Rapid strep antigen testing in adults reduces inappropriate prescribing: **Confirmed**
- Acute bacterial rhinosinusitis duration of 5-7 days (adults) and 10-14 days (children): **Confirmed**

**Verdict: CLEAN.** No errors detected at any phase.

---

### Citation 2: de la Poza Abad et al., JAMA Internal Medicine, 2016

> de la Poza Abad M, Mas Dalmau G, Moreno Bakedano M, et al. Prescription Strategies in Acute Uncomplicated Respiratory Infections: A Randomized Clinical Trial. *JAMA Internal Medicine*. 2016;176(1):21-9. doi:10.1001/jamainternmed.2015.7088.

| Phase | Result |
|-------|--------|
| Phase 0 | DOI exists in CrossRef |
| Phase 1 | Resolves to JAMA Network (PMID 26719947) |
| Phase 2 | **FAIL: Two statistics misattributed** |
| Phase 3 | All metadata correct |

**Error detail:**

The OpenEvidence response attributes two U.S. national prescribing rates to this paper:

> "approximately 60% of patients with sore throat and 71% with acute bronchitis receive antibiotics" [2]

The de la Poza Abad paper is a **Spanish randomized clinical trial** comparing delayed, immediate, and no-prescribing strategies. It does not report U.S. national prescribing rates.

**Actual sources for these statistics:**

| Statistic | Actual Source | Citation |
|-----------|--------------|----------|
| 60% of sore throat visits receive antibiotics | Barnett & Linder, *JAMA Internal Medicine*, 2014 | doi:10.1001/jamainternmed.2013.11673 |
| 71% of acute bronchitis visits receive antibiotics | Barnett & Linder, *JAMA*, 2014 | doi:10.1001/jama.2014.5266 |

Both figures come from analyses of U.S. National Ambulatory Medical Care Survey (NAMCS) data. Neither originates from the cited Spanish trial.

**Error classification:** CLAIM_MISMATCH (real statistics from the field attributed to the wrong paper)

**Clinical impact:** A physician reading this citation and wanting to verify the 60%/71% figures would not find them in the de la Poza Abad paper. This erodes trust in the platform's citation accuracy.

---

### Citation 3: Kuijpers et al., The Lancet Infectious Diseases, 2025

> Kuijpers SME, Buis DTP, Ziesemer KA, et al. The Evidence Base for the Optimal Antibiotic Treatment Duration of Upper and Lower Respiratory Tract Infections: An Umbrella Review. *The Lancet Infectious Diseases*. 2025;25(1):94-113. doi:10.1016/S1473-3099(24)00456-0.

| Phase | Result |
|-------|--------|
| Phase 0 | DOI exists in CrossRef |
| Phase 1 | Resolves to The Lancet (PMID 39243792) |
| Phase 2 | Claims substantively supported |
| Phase 3 | All metadata correct |

**Claims verified:**

- Evidence supports shorter treatment durations: **Confirmed** (paper concludes: "available evidence for non-ICU CAP and AECOPD supports a short-course treatment duration of 5 days in patients who have clinically improved")
- Implementation gaps more significant than knowledge gaps: **Confirmed** (reasonable paraphrase of: "efforts of the scientific community should be directed at implementing this evidence in daily practice")
- Stewardship aims to optimize outcomes while minimizing resistance: **Supported** (paper discusses reduced antibiotic exposure and resistance selection, though this is general stewardship framing rather than a specific finding of the umbrella review)

**Verdict: CLEAN** with minor caveat that stewardship framing is slightly broader than the paper's specific scope (treatment duration evidence).

---

### Citation 4: Harris et al., Annals of Internal Medicine, 2016

> Harris AM, Hicks LA, Qaseem A. Appropriate Antibiotic Use for Acute Respiratory Tract Infection in Adults: Advice for High-Value Care From the American College of Physicians and the Centers for Disease Control and Prevention. *Annals of Internal Medicine*. 2016;164(6):425-34. doi:10.7326/M15-1840.

| Phase | Result |
|-------|--------|
| Phase 0 | DOI exists in CrossRef |
| Phase 1 | Resolves to ACP Journals (PMID 26785402) |
| Phase 2 | **FAIL: Citation overloading, unverified statistic** |
| Phase 3 | All metadata correct |

**Error detail:**

This single ACP/CDC guideline paper is used as the citation for claims that originate from multiple different studies:

| Claim in OpenEvidence Response | Attributed to [4] | Actual Source |
|-------------------------------|-------------------|---------------|
| ABRS criteria (>10 days, high fever >=3 days, double-sickening) | Supported | Harris 2016 discusses these criteria |
| Labeling bronchitis as "chest cold" achieves **85% decrease** in prescribing | **Unverified** | The "chest cold" labeling concept traces to Phillips & Hickner 2005 (*J Am Board Fam Pract*). An ~81% relative reduction is from Meeker et al. 2016 (*JAMA*). The specific "85% decrease" figure does not cleanly match any single verified source. |
| Audit and feedback with peer comparison | **Misattributed** | Meeker et al., *JAMA*, 2016, doi:10.1001/jama.2016.0275 |
| First-line agents for otitis media | **Misattributed** | IDSA/AAO-HNS clinical practice guidelines, not this ACP/CDC advice paper |
| Patient satisfaction depends on communication, not antibiotics | Plausible | General finding in stewardship literature; Harris 2016 likely references but does not generate this evidence |

**Error classification:** CLAIM_MISMATCH + CITATION_OVERLOADING + possible FABRICATED_STATISTIC

The "85% decrease in antibiotic prescribing" figure is the most concerning finding. It does not cleanly trace to any single peer-reviewed source. It may be a garbled conflation of the ~81% relative reduction from Meeker et al. 2016 (a peer comparison intervention, not a labeling intervention). If a clinician implemented a "chest cold" labeling strategy expecting an 85% prescribing reduction based on this citation, they would be acting on an unverifiable number.

---

### Citation 5: Libman et al., Annals of Internal Medicine, 2017

> Libman H, Brockmeyer DM, Gold HS. Should We Prescribe Antibiotics to This Patient With Persistent Upper Respiratory Symptoms?: Grand Rounds Discussion From Beth Israel Deaconess Medical Center. *Annals of Internal Medicine*. 2017;166(3):201-208. doi:10.7326/M16-2766.

| Phase | Result |
|-------|--------|
| Phase 0 | DOI exists in CrossRef |
| Phase 1 | Resolves to ACP Journals |
| Phase 2 | Claim supported |
| Phase 3 | All metadata correct |

**Claims verified:**

- ABRS diagnostic criteria (persistent >10 days, high fever with purulent discharge >=3 days, double-sickening): **Confirmed.** Grand rounds discussion covers all three criteria.

**Verdict: CLEAN.** Note: these diagnostic criteria originate from earlier IDSA guidelines (Chow et al. 2012). Libman 2017 is a clinical discussion applying them, not the original source. The citation is accurate for a secondary discussion.

---

### Citation 6: File & Ramirez, NEJM, 2023

> File TM, Ramirez JA. Community-Acquired Pneumonia. *The New England Journal of Medicine*. 2023;389(7):632-641. doi:10.1056/NEJMcp2303286.

| Phase | Result |
|-------|--------|
| Phase 0 | DOI exists in CrossRef |
| Phase 1 | Resolves to NEJM (PMID 37585629) |
| Phase 2 | Claim supported with completeness caveat |
| Phase 3 | All metadata correct |

**Claims verified:**

- CAP treatment with amoxicillin, doxycycline, or macrolides: **Confirmed** (NEJM Clinical Practice review covering ATS/IDSA 2019 guideline recommendations)

**Clinical accuracy caveat:** The macrolide recommendation carries a significant restriction that the OpenEvidence response omits. Macrolide monotherapy is recommended only conditionally, in areas with pneumococcal macrolide resistance rates below 25%. In the United States, macrolide resistance exceeds 30% in most regions. An unqualified "macrolides" recommendation without this restriction could lead to inappropriate empiric therapy.

**Verdict: CLEAN** from a citation accuracy standpoint. The clinical completeness gap (missing resistance threshold) is a content quality issue rather than a citation error.

---

### Citation 7: Davidson et al., Infection Control and Hospital Epidemiology, 2023

> Davidson LE, Gentry EM, Priem JS, Kowalkowski M, Spencer MD. A Multimodal Intervention to Decrease Inappropriate Outpatient Antibiotic Prescribing for Upper Respiratory Tract Infections in a Large Integrated Healthcare System. *Infection Control and Hospital Epidemiology*. 2023;44(3):392-399. doi:10.1017/ice.2022.83.

| Phase | Result |
|-------|--------|
| Phase 0 | DOI exists in CrossRef |
| Phase 1 | Resolves to Cambridge Core (PMID 35491941) |
| Phase 2 | **FAIL: Intervention type mischaracterized** |
| Phase 3 | All metadata correct |

**Error detail:**

The OpenEvidence response describes:

> "Electronic decision support systems and provider dashboards have demonstrated significant reductions in inappropriate prescribing." [7]

The Davidson et al. intervention was the CHOSEN program: a **web-based provider prescribing dashboard** (retrospective feedback on past prescribing patterns) combined with patient/provider educational materials. This is fundamentally different from "electronic decision support systems," which implies real-time alerts integrated into the EHR at point of care.

| Term Used | What It Implies | What Actually Happened |
|-----------|----------------|----------------------|
| Electronic decision support systems | Real-time CDS alerts during patient encounter | Retrospective prescribing dashboard reviewed after encounters |

The 16.6-20.4% reduction range across outpatient specialties is accurately reported.

**Error classification:** CLAIM_MISMATCH (intervention type mischaracterized)

**Clinical impact:** An implementation team reading this might allocate resources for real-time CDS infrastructure when the evidence actually supports a simpler, retrospective dashboard approach. The intervention characterization matters because it determines what health systems actually build.

---

### Citation 8: Stenehjem et al., JAMA Network Open, 2023

> Stenehjem E, Wallin A, Willis P, et al. Implementation of an Antibiotic Stewardship Initiative in a Large Urgent Care Network. *JAMA Network Open*. 2023;6(5):e2313011. doi:10.1001/jamanetworkopen.2023.13011.

| Phase | Result |
|-------|--------|
| Phase 0 | DOI exists in CrossRef |
| Phase 1 | Resolves to JAMA Network (PMID 37166794) |
| Phase 2 | **FAIL: Statistic conflation** |
| Phase 3 | All metadata correct |

**Error detail:**

The OpenEvidence response states:

> "A large urgent care network demonstrated sustained reductions in antibiotic prescribing from 48% to 26% using dashboard feedback combined with education." [8]

The actual data from the paper:

| Period | Antibiotic Prescribing Rate | Study Phase |
|--------|---------------------------|-------------|
| Baseline | 47.8% | Pre-intervention |
| Intervention period | **33.3%** | Primary outcome |
| Sustainability period | 25.5% | Post hoc analysis, 1-2 years later |

The OpenEvidence response collapses two distinct time periods into a single "48% to 26%" figure. The direct intervention result was 48% to 33% (a 31% relative reduction). The 26% figure comes from a separate sustainability period analysis. Presenting these as one effect nearly doubles the apparent magnitude of the immediate intervention.

Additionally, "dashboard feedback combined with education" undersells a four-component intervention:
1. Clinician and patient education
2. EHR tools
3. Transparent clinician benchmarking dashboard
4. Media campaigns

The study also incorporated financial incentives (stewardship measures tied to quality metrics with financial consequences). Omitting this component misrepresents what drove the results.

**Error classification:** CLAIM_MISMATCH + misleading statistic presentation

**Clinical impact:** A medical director reading "48% to 26% reduction" would expect near-halving of antibiotic prescribing from implementing a dashboard with education. The actual immediate effect was a reduction to 33%. The additional decline to 26% required sustained effort over one to two additional years, plus financial incentives. Planning based on the conflated figure would set unrealistic expectations.

---

### Citation 9: Gerber et al., JAMA, 2013

> Gerber JS, Prasad PA, Fiks AG, et al. Effect of an Outpatient Antimicrobial Stewardship Intervention on Broad-Spectrum Antibiotic Prescribing by Primary Care Pediatricians: A Randomized Trial. *JAMA*. 2013;309(22):2345-52. doi:10.1001/jama.2013.6287.

| Phase | Result |
|-------|--------|
| Phase 0 | DOI exists in CrossRef |
| Phase 1 | Resolves to JAMA (PMID 23757082) |
| Phase 2 | N/A (appears in figures section with no specific inline claim) |
| Phase 3 | All metadata correct |

**Verdict: CLEAN.** Landmark pediatric stewardship RCT. Metadata fully verified. No specific inline claim to assess.

---

## Error Pattern Analysis

### Distribution of Error Types

| Error Category | Citations Affected | Pipeline Phase |
|----------------|-------------------|----------------|
| Claim-citation misattribution | 2, 4 | Phase 2 |
| Statistic conflation | 8 | Phase 2 |
| Intervention mischaracterization | 7 | Phase 2 |
| Citation overloading | 4 | Phase 2 |
| Possible fabricated statistic | 4 (the "85%" figure) | Phase 2 |

Every error is a Phase 2 finding. Phases 0, 1, and 3 returned clean results across all 9 citations. This confirms the core finding of the Citation Verification Pipeline: the errors that matter most are invisible to automated checking.

### Patterns Observed

**1. Claim-citation misattribution.** Real statistics from the broader antibiotic stewardship literature are bundled under whichever citation happens to be nearby. The 60% (sore throat) and 71% (bronchitis) prescribing rates exist in published research (Barnett & Linder, 2014), but OpenEvidence attributes them to a Spanish RCT that never reported those figures.

**2. Citation overloading.** A single guideline paper (Harris et al. 2016) is used as the citation for findings from at least three separate studies. This makes the citation look well-sourced while obscuring that the actual evidence comes from different research teams with different methodologies.

**3. Statistic conflation.** Two distinct study periods (intervention vs. sustainability) are collapsed into a single figure, nearly doubling the apparent effect size. This is not a factual error in the narrow sense (both numbers are in the paper), but the presentation misleads about what to expect from the intervention.

**4. Intervention mischaracterization.** A retrospective prescribing dashboard is described as "electronic decision support systems," implying real-time CDS functionality that did not exist. This matters for implementation decisions.

**5. Unverifiable statistic.** The "85% decrease in antibiotic prescribing" from labeling bronchitis as "chest cold" does not trace to any single verified source. It may be a garbled version of the ~81% relative reduction from Meeker et al. 2016, which studied a different intervention (peer comparison, not labeling). If this figure is fabricated, it is the most clinically consequential error in the response.

### What Standard Verification Misses

| Verification Method | Errors Detected | Errors Missed |
|--------------------|-----------------|-|
| URL/link checking (Phase 0-1 only) | 0/5 | 5/5 (100% miss rate) |
| URL + metadata checking (Phase 0-1-3) | 0/5 | 5/5 (100% miss rate) |
| Full pipeline including content verification (Phase 0-4) | 5/5 | 0/5 |

A standard citation audit checking URL resolution, DOI validity, and metadata accuracy would have returned a **perfect score** for this OpenEvidence response. Every error requires reading the cited paper and comparing its actual findings to the inline claim.

---

## Implications for Clinical AI Platforms

### The Invisible Error Problem

Citation errors in clinical AI outputs fall into two categories:

1. **Visible errors:** Broken links, 404s, fabricated DOIs. These are easy to detect automatically and account for approximately 21% of citation errors in LLM-generated content.

2. **Invisible errors:** Valid citations that do not support the specific claim. These require content-level verification and account for approximately 79% of errors.

OpenEvidence's citation infrastructure eliminates visible errors entirely. Every citation in this response points to a real paper with correct metadata. The platform's integration with NEJM, JAMA, and NCCN content libraries ensures bibliographic accuracy.

The invisible errors persist because they exist at a different layer: the relationship between what the paper says and what the AI claims it says. Addressing this requires a verification system that operates at the content-claim alignment level, not the URL resolution level.

### What a Content-Level Verification System Would Catch

For this specific response, an automated content-claim alignment system would need to:

1. **Detect misattributed statistics:** Flag when a specific percentage (60%, 71%) appears in the response text but not in the cited paper's abstract or findings
2. **Detect statistic conflation:** Flag when a cited figure spans two different study periods or populations without explicit qualification
3. **Detect intervention mischaracterization:** Flag when the description of an intervention (e.g., "electronic decision support") does not match the intervention type documented in the cited paper's methods section
4. **Detect citation overloading:** Flag when a single citation is used to support more than 3-4 distinct claims, indicating that multiple source papers may be collapsed into one citation

### The Verification Gap as a Product Risk

The PMC-indexed paper "OpenEvidence: Enhancing Medical Student Clinical Rotations With AI but With Limitations" (January 2025) already documents citation hallucination as a limitation. The findings in this audit confirm that the vulnerability extends beyond fabricated citations to a subtler category: accurate citations with inaccurate claim-citation alignment.

This category is harder to detect, harder to prevent, and harder to explain to users. A physician who clicks a JAMA Network Open citation and finds the paper exists may assume the attributed finding is correct. They would need to read the full paper and compare its specific data to the AI's claim to discover the discrepancy.

---

## Appendix: Verified Correct Citations

For completeness, the following citations passed all five phases without issues:

| # | Citation | All Phases Pass |
|---|----------|----------------|
| 1 | Sur & Plesa, AFP 2022 | Yes |
| 3 | Kuijpers et al., Lancet ID 2025 | Yes (minor scope caveat) |
| 5 | Libman et al., Ann Intern Med 2017 | Yes |
| 6 | File & Ramirez, NEJM 2023 | Yes (clinical completeness caveat) |
| 9 | Gerber et al., JAMA 2013 | Yes (no inline claim to verify) |

---

## Appendix: Methodology Reference

This audit was conducted using the Five-Phase Citation Verification Pipeline documented in `METHODOLOGY.md`. The pipeline, error taxonomy, and defense architecture are available at:

**Repository:** [citation-audit](https://github.com/BryanTegomoh/citation-audit)

The pipeline was developed through systematic verification of 150+ citations across 22 medical specialty chapters, identifying 21 distinct failure modes (Gaps 1-21) documented in the methodology. This OpenEvidence audit demonstrates the pipeline's application to clinical AI platform outputs, confirming that content-level verification (Phase 2) is the critical layer for systems that have already solved URL-level accuracy.

---

*Audit conducted March 4, 2026. All verification searches executed in real time against PubMed, CrossRef, and publisher websites.*
