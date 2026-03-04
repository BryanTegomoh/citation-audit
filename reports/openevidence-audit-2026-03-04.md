# OpenEvidence Citation Accuracy Audit

**Date:** March 4, 2026
**Methodology:** Five-Phase Citation Verification Pipeline v3.3
**Target:** OpenEvidence response on antibiotic stewardship strategies in outpatient respiratory infections
**Source:** [OpenEvidence query](https://www.openevidence.com/ask/d252c9f9-08ed-4db8-b6ab-8f0fd13ce058)
**Auditor:** Bryan Tegomoh, MD, MPH
**Verification pass:** Second pass (comprehensive re-verification of all 9 citations)

---

## Summary

| Metric | Result |
|--------|--------|
| Citations analyzed | 9 |
| Phase 0-1 pass (DOI exists, URL resolves) | 9/9 (100%) |
| Phase 2-3 pass (claims supported, metadata correct) | 3/9 (33%) |
| Citations with content-level issues | 6/9 (67%) |
| Fabricated papers | 0 |
| Fabricated DOIs | 0 |
| Distinct failure modes identified | 12 |
| Misattributed statistics | 2 |
| Statistic conflation | 1 |
| Intervention mischaracterization | 2 |
| Citation overloading | 1 |
| Decoration citation | 1 |
| Denominator shift | 1 |
| Qualifier/drawback omissions | 2 |
| Ambiguous data presentation | 1 |

**Bottom line:** Every citation points to a real paper with accurate metadata. A standard link-check audit would return a perfect score. Content-level verification reveals that 67% of citations have claim-citation alignment problems or citation usage issues, ranging from misattributed statistics to subtle reframing of source material. These are the errors that reach clinicians.

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

**Second-pass methodology:** All 9 citations were independently re-verified as if encountering them for the first time. Each verification report documents the complete evidence chain. The first pass identified 4 citations with errors; the second pass confirmed all 4 and identified additional failure modes in 2 citations previously classified as clean, plus 1 decoration citation.

---

## Citation-by-Citation Results

### Citation 1: Sur & Plesa, American Family Physician, 2022

> Sur DKC, Plesa ML. Antibiotic Use in Acute Upper Respiratory Tract Infections. *American Family Physician*. 2022;106(6):628-636.

| Phase | Result |
|-------|--------|
| Phase 0 | N/A (AFP does not assign DOIs, standard for this journal) |
| Phase 1 | Paper confirmed at PubMed (PMID 36521460) and AAFP website |
| Phase 2 | **PARTIALLY CLEAN: Core claims confirmed, subtle distortions identified** |
| Phase 3 | Authors, journal, year, volume, pages: all correct |

**Claims verified against AAFP full-text article:**

| # | Claim | Verdict | Notes |
|---|-------|---------|-------|
| 1 | CDC high-priority targets (URIs, pharyngitis, rhinosinusitis, AOM) | Confirmed | Minor paraphrase; accurate |
| 2 | GAS pharyngitis treatment with amoxicillin/penicillin V | Confirmed | Paper says "hastens clinical resolution"; OE says "reduces symptom duration." Paper qualifies rheumatic fever as "rare complications"; OE drops "rare" |
| 3 | Delayed prescribing reduces antibiotic use | Confirmed | **Drawback omitted:** Paper explicitly states delayed prescribing "decreased patient satisfaction and increased symptom duration." OE presents the strategy without its documented trade-offs |
| 4 | Combining positive + negative recommendations decreases prescribing and improves satisfaction | Confirmed | Near-verbatim match |
| 5 | Less than 1% penicillin allergy confirmed | **Denominator shifted** | **Paper says:** "less than 1% of the population has a confirmed penicillin allergy." **OE says:** "less than 1% of patients reporting penicillin allergy have confirmed allergy." Different denominators, different math (see analysis below) |
| 6 | PEN-FAST tool as validated point-of-care decision rule | Confirmed | Near-verbatim |
| 7 | Rapid strep testing reduces inappropriate prescribing | Confirmed | Minor tense change; OE omits "without adverse consequences" |
| 8 | Rhinosinusitis treatment duration 5-7 days (adults), 10-14 days (children) | Confirmed | **Ambiguity:** These are TREATMENT durations for amoxicillin/clavulanate, not illness durations. OE phrasing is ambiguous |

**Failure modes identified:**

**1. DENOMINATOR_SHIFT (Claim 5 - penicillin allergy statistic).**
The paper states: "Approximately 10% of people in the United States report having a penicillin allergy; however, less than 1% of the population has a confirmed penicillin allergy." This compares two population-level rates: 10% self-reported vs. <1% confirmed, both using the general population as denominator.

OpenEvidence reframes this as: "less than 1% of patients reporting penicillin allergy have confirmed allergy." This changes the denominator from "the population" to "patients reporting allergy," which would mean <1% of 10% = <0.1% of the population. The mathematical meaning shifts by an order of magnitude.

Note: The "<1% of reporters" framing does appear in other sources (e.g., Shenoy et al., JAMA 2019, using skin testing data), but it is not what Sur & Plesa 2022 states. OpenEvidence may have conflated framings from different papers while attributing the result to this one.

**2. DRAWBACK_OMISSION (Claim 3 - delayed prescribing).**
The paper provides a balanced assessment: delayed prescribing "reduced antibiotic use but also decreased patient satisfaction and increased symptom duration." OpenEvidence presents only the benefit (reduced use) without the documented trade-offs (decreased satisfaction, increased symptom duration). A clinician implementing this strategy based on the OE summary would not anticipate the trade-offs the paper identifies.

**3. QUALIFIER_OMISSION (Claim 2 - rheumatic fever).**
The paper states treatment "helps prevent the rare complications of acute rheumatic fever." OpenEvidence drops "rare," which subtly overstates the clinical significance of the prevention benefit. While acute rheumatic fever prevention is a real indication for GAS pharyngitis treatment, characterizing it without the "rare" qualifier shifts the risk-benefit framing.

**4. AMBIGUITY (Claim 8 - treatment duration).**
The paper clearly states these are antibiotic treatment durations for amoxicillin/clavulanate. The OpenEvidence phrasing "duration of 5-7 days" could be read as illness duration rather than treatment duration.

**Additional checks:**
- "85% decrease": NOT in this paper. The 85% figure originates from Mangione-Smith et al. 2015. If attributed to Sur & Plesa, this would be misattribution.
- "Chest cold" language: NOT in this paper. This terminology comes from Phillips & Hickner 2005 (*JABFM*).

**Verdict: Four subtle failure modes detected.** None are fabrications; all involve reframing, omission, or denominator shifts that change the practical meaning of accurate underlying facts. Individually minor; collectively they demonstrate a pattern of selective presentation.

**Full verification report:** [citation1_verification.md](verification/citation1_verification.md)

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

The de la Poza Abad paper is a **Spanish randomized clinical trial** comparing delayed, immediate, and no-prescribing strategies across 23 primary care centers. It enrolled 398 adults and measured symptom duration, severity, and antibiotic consumption across trial arms. It does not report U.S. national prescribing rates. The figures "60%" and "71%" do not appear in this paper.

**Actual sources for these statistics:**

| Statistic | Actual Source | Citation |
|-----------|--------------|----------|
| 60% of sore throat visits receive antibiotics | Barnett & Linder, *JAMA Internal Medicine*, 2014 | doi:10.1001/jamainternmed.2013.11673 |
| 71% of acute bronchitis visits receive antibiotics | Barnett & Linder, *JAMA*, 2014 | doi:10.1001/jama.2014.5266 |

Both figures come from analyses of U.S. National Ambulatory Medical Care Survey (NAMCS) data, 1996-2010. Neither originates from the cited Spanish trial. Confirmed: de la Poza Abad does not cite either Barnett & Linder paper in its reference list.

**Error classification:** CLAIM_MISMATCH (cross-paper citation swap: real statistics from the field attributed to the wrong paper)

**Why this error is dangerous:** This error would pass basic verification checks. The DOI resolves correctly. The paper is real and published in a top-tier journal. The topic (antibiotic prescribing for respiratory infections) is adjacent. The statistics themselves are accurate. Only content-level verification (reading the paper and confirming it contains the specific claim) catches this.

**Full verification report:** [citation2_verification.md](verification/citation2_verification.md)

---

### Citation 3: Kuijpers et al., The Lancet Infectious Diseases, 2025

> Kuijpers SME, Buis DTP, Ziesemer KA, et al. The Evidence Base for the Optimal Antibiotic Treatment Duration of Upper and Lower Respiratory Tract Infections: An Umbrella Review. *The Lancet Infectious Diseases*. 2025;25(1):94-113. doi:10.1016/S1473-3099(24)00456-0.

| Phase | Result |
|-------|--------|
| Phase 0 | DOI exists in CrossRef |
| Phase 1 | Resolves to The Lancet (PMID 39243792) |
| Phase 2 | Claims substantively supported |
| Phase 3 | All metadata correct (online Sept 5, 2024; print Jan 2025, Vol 25 Issue 1) |

**Claims verified:**

| Claim | Verdict | Notes |
|-------|---------|-------|
| Evidence supports shorter treatment durations | Confirmed | Paper concludes 5-day courses for non-ICU CAP and AECOPD in clinically improved patients. Evidence insufficient for HAP, sinusitis, pharyngotonsillitis with penicillin |
| Implementation gaps more significant than knowledge gaps | Confirmed | This is the paper's central thesis: the umbrella review was designed to distinguish knowledge gaps from implementation gaps |
| Stewardship aims to optimize outcomes while minimizing resistance | Partially confirmed | Background framing language, not a finding of the review; appropriately used as context by OpenEvidence |

**Condition-specific nuances OpenEvidence omits:**
- Non-ICU CAP: Moderate-quality evidence supports 5 days (not shorter)
- AECOPD: Sufficient evidence for 5 days
- Hospital-acquired pneumonia: Evidence absent
- Acute sinusitis: Insufficient data
- Pharyngotonsillitis: Short-course cephalosporin supported, but NOT short-course penicillin

**Verdict: CLEAN.** One of the stronger citation attributions in the audit. The paper's central argument (implementation gap vs. knowledge gap) is correctly identified and attributed.

**Full verification report:** [citation3_verification.md](verification/citation3_verification.md)

---

### Citation 4: Harris et al., Annals of Internal Medicine, 2016

> Harris AM, Hicks LA, Qaseem A. Appropriate Antibiotic Use for Acute Respiratory Tract Infection in Adults: Advice for High-Value Care From the American College of Physicians and the Centers for Disease Control and Prevention. *Annals of Internal Medicine*. 2016;164(6):425-34. doi:10.7326/M15-1840.

| Phase | Result |
|-------|--------|
| Phase 0 | DOI exists in CrossRef |
| Phase 1 | Resolves to ACP Journals (PMID 26785402) |
| Phase 2 | **FAIL: Citation overloading, intervention misattribution** |
| Phase 3 | All metadata correct |

**Error detail:**

This single ACP/CDC guideline paper is used as the citation for claims that originate from multiple different studies:

| Claim in OpenEvidence Response | Attributed to [4] | Actual Source |
|-------------------------------|-------------------|---------------|
| ABRS criteria (>10 days, high fever >=3 days, double-sickening) | Supported | Harris 2016 discusses these criteria (originally from Chow et al. 2012 IDSA guidelines) |
| Labeling bronchitis as "chest cold" achieves **85% decrease** in prescribing | **Intervention misattributed** | The 85% figure is real: Mangione-Smith et al. 2015 (*Annals of Family Medicine*) found aRR 0.15 (85% reduction) when providers combined symptomatic therapy advice with explanation of why antibiotics were not needed. Harris et al. 2016 cites this correctly as reference (64). OpenEvidence misattributes the 85% to "chest cold" labeling, which is a different intervention (Phillips & Hickner 2005, *JABFM*) that measured patient satisfaction, not prescribing rates. |
| Audit and feedback with peer comparison | **Misattributed** | Meeker et al., *JAMA*, 2016, doi:10.1001/jama.2016.0275. Harris 2016 does not describe peer comparison as a stewardship intervention. |
| Patient satisfaction depends on communication, not antibiotics | Plausible | General finding in stewardship literature; Harris 2016 likely references but does not generate this evidence |

**Error classification:** CITATION_OVERLOADING + INTERVENTION_MISATTRIBUTION

The 85% figure traces to Mangione-Smith et al. 2015 (*Annals of Family Medicine*), which found an adjusted risk ratio of 0.15 when providers combined positive treatment recommendations (symptomatic therapy advice) with negative treatment recommendations (explaining why antibiotics were not needed). Harris et al. 2016 accurately cites this as reference (64). However, the OpenEvidence response attributes this 85% reduction to "labeling bronchitis as 'chest cold,'" which is a distinct intervention studied by Phillips & Hickner 2005. That study measured patient satisfaction with diagnosis labels, not prescribing rates. A clinician implementing a "chest cold" labeling strategy and expecting an 85% prescribing reduction would be acting on a misattributed finding: the 85% comes from a combined communication intervention, not diagnostic relabeling.

**Audit correction:** The first-pass audit listed "first-line agents for otitis media" as misattributed to [4]. Three independent reviews of the OpenEvidence response confirmed that otitis media is mentioned only once, attributed to [1], not [4]. This was a false positive in our own audit, now removed.

**Full verification report:** [citation4_verification.md](verification/citation4_verification.md)

---

### Citation 5: Libman et al., Annals of Internal Medicine, 2017

> Libman H, Brockmeyer DM, Gold HS. Should We Prescribe Antibiotics to This Patient With Persistent Upper Respiratory Symptoms?: Grand Rounds Discussion From Beth Israel Deaconess Medical Center. *Annals of Internal Medicine*. 2017;166(3):201-208. doi:10.7326/M16-2766.

| Phase | Result |
|-------|--------|
| Phase 0 | DOI exists in CrossRef |
| Phase 1 | Resolves to ACP Journals (PMID 28166559) |
| Phase 2 | Claim supported |
| Phase 3 | All metadata correct |

**Claims verified:**

- ABRS diagnostic criteria (persistent >10 days, high fever with purulent discharge >=3 days, double-sickening): **Confirmed.** Grand Rounds discussion covers all three criteria, cites both Chow et al. 2012 (IDSA guidelines, reference r10) and Harris et al. 2016 (reference r7).

**Citation usage pattern:** Citation [5] appears only once in the OpenEvidence response, always paired with [4] as [4-5]. It is never used standalone. This means it adds no independent evidentiary value: removing [5] would not reduce the response's evidential coverage.

**Verdict: CLEAN.** Accurate secondary citation. The Grand Rounds format is a clinical teaching discussion applying established guidelines, not original research.

**Full verification report:** [citation5_verification.md](verification/citation5_verification.md)

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

- CAP treatment with amoxicillin, doxycycline, or macrolides for healthy adults: **Confirmed** (NEJM Clinical Practice review covering ATS/IDSA 2019 guideline recommendations)
- <25% pneumococcal macrolide resistance qualifier: **Likely present.** This threshold originates from the ATS/IDSA 2019 guidelines (Metlay et al., *Am J Respir Crit Care Med*. 2019;200(7):e45-e67). Thomas File was a member of the ATS/IDSA guideline committee. As a Clinical Practice review, this article presents those guideline recommendations.

**Clinical accuracy caveat:** In the United States, pneumococcal macrolide resistance averages approximately 30%, exceeding the 25% threshold. Macrolide monotherapy is therefore inappropriate in most US settings. The OpenEvidence response includes the <25% qualifier, which is clinically appropriate.

**Verdict: CLEAN** from a citation accuracy standpoint. The <25% threshold is a guideline recommendation from ATS/IDSA 2019 that File & Ramirez 2023 reviews; it is not independent research from this paper.

**Full verification report:** [citation6_verification.md](verification/citation6_verification.md)

---

### Citation 7: Davidson et al., Infection Control and Hospital Epidemiology, 2023

> Davidson LE, Gentry EM, Priem JS, Kowalkowski M, Spencer MD. A Multimodal Intervention to Decrease Inappropriate Outpatient Antibiotic Prescribing for Upper Respiratory Tract Infections in a Large Integrated Healthcare System. *Infection Control and Hospital Epidemiology*. 2023;44(3):392-399. doi:10.1017/ice.2022.83.

| Phase | Result |
|-------|--------|
| Phase 0 | DOI exists in CrossRef |
| Phase 1 | Resolves to Cambridge Core (PMID 35491941; epub May 2022, print March 2023) |
| Phase 2 | **FAIL: Intervention type mischaracterized** |
| Phase 3 | All metadata correct |

**Error detail:**

The OpenEvidence response describes:

> "Electronic decision support systems and provider dashboards have demonstrated significant reductions in inappropriate prescribing." [7]

The Davidson et al. intervention was the **CHOSEN program** (Carolinas Healthcare Outpatient Antimicrobial Stewardship Empowerment Network): a **retrospective web-based prescribing dashboard** built in Microsoft Power BI, combined with patient/provider educational materials, targeted on-site education, and consumer outreach. The dashboard was:

- **Retrospective:** Displayed historical prescribing data, not real-time guidance
- **Updated monthly:** Not during patient encounters
- **Separate from the EHR:** A standalone web-based analytics tool, not integrated into clinical workflow
- **Self-accessed:** Providers voluntarily reviewed their data, not pushed alerts

"Electronic decision support systems" implies real-time, EHR-integrated, point-of-care alerts that interrupt the clinical workflow during prescribing decisions. This is a fundamentally different category of technology.

| Term Used | What It Implies | What Actually Happened |
|-----------|----------------|----------------------|
| Electronic decision support systems | Real-time CDS alerts during patient encounter | Retrospective Power BI dashboard reviewed after encounters |
| Provider dashboards with peer comparison | Structured audit-and-feedback with social norms | Voluntary self-service analytics enabling implicit comparison |

The 16.6-20.4% reduction range across outpatient specialties is accurately reported. The study also found higher rates of first-line antibiotic selection (83.1% vs. 77.7%, P = 0.024) and shorter antibiotic duration (9.28 vs. 9.79 days, P < 0.001) in intervention clinics.

No financial incentives were part of the CHOSEN program (unlike Citation [8]).

**Error classification:** CLAIM_MISMATCH (intervention type mischaracterized)

**Clinical impact:** An implementation team reading this might allocate resources for real-time CDS infrastructure when the evidence actually supports a simpler, retrospective dashboard approach. The CHOSEN model's success came from making prescribing data transparent and accessible, combined with education and on-site coaching. This is a behavioral/informational intervention, not a technology-interruption intervention.

**Full verification report:** [citation7_verification.md](verification/citation7_verification.md)

---

### Citation 8: Stenehjem et al., JAMA Network Open, 2023

> Stenehjem E, Wallin A, Willis P, et al. Implementation of an Antibiotic Stewardship Initiative in a Large Urgent Care Network. *JAMA Network Open*. 2023;6(5):e2313011. doi:10.1001/jamanetworkopen.2023.13011.

| Phase | Result |
|-------|--------|
| Phase 0 | DOI exists in CrossRef |
| Phase 1 | Resolves to JAMA Network (PMID 37166794; PMC10176123 open access) |
| Phase 2 | **FAIL: Compound misrepresentation (statistic conflation + intervention simplification + financial incentive omission)** |
| Phase 3 | All metadata correct |

**Error detail:**

The OpenEvidence response states:

> "A large urgent care network demonstrated sustained reductions in antibiotic prescribing from 48% to 26% using dashboard feedback combined with education." [8]

The actual data from the paper:

| Period | Dates | Antibiotic Prescribing Rate | Study Phase |
|--------|-------|---------------------------|-------------|
| Baseline | July 2018 - June 2019 | **47.8%** | Pre-intervention |
| Intervention | July 2019 - June 2020 | **33.3%** | Primary outcome (14.5 pp reduction) |
| Sustainability | July 2020 - June 2021 | **25.5%** | Post hoc analysis, 1-2 years later (additional 7.8 pp) |

**Three simultaneous misrepresentations:**

**1. TEMPORAL_CONFLATION.** The "48% to 26%" figure collapses a three-year, two-phase trajectory into a single data point. The direct intervention result was 47.8% to 33.3% (a 14.5 percentage point reduction). The further decline to 25.5% occurred during a separate sustainability period one to two years later. Presenting these as one effect nearly doubles the apparent magnitude of the immediate intervention.

**2. INTERVENTION_SIMPLIFICATION.** "Dashboard feedback combined with education" omits two of four intervention components:

| Component | Included in OE Summary? |
|-----------|------------------------|
| Clinician and patient education | Yes |
| Transparent clinician benchmarking dashboard | Yes |
| EHR tools (clinical decision support alerts, delayed Rx options, templated notes) | No |
| Media campaigns (television, radio, social media, in-clinic signage) | No |

**3. FINANCIAL_INCENTIVE_OMISSION.** Urgent care leadership independently introduced a **financial incentive** linking clinician compensation to antibiotic prescribing rates (clinicians prescribing antibiotics in fewer than 50% of respiratory encounters received increased compensation eligibility). The paper explicitly acknowledges this as a limitation: "the impact of stewardship intervention and quality measures linked to provider compensation could not be evaluated independently." OpenEvidence makes no mention of this financial component, which represents an entirely different behavior change mechanism (extrinsic motivation vs. education/awareness).

**Error classification:** COMPOUND_MISREPRESENTATION (temporal conflation + intervention simplification + financial incentive omission)

**Additional context:** The sustainability period (July 2020 - June 2021) overlapped entirely with COVID-19, which likely reduced respiratory visits and may have independently influenced prescribing patterns. Sensitivity analyses in the paper found COVID-19 did not significantly alter primary findings, but this context is relevant to interpreting the sustainability-period rates.

**Clinical impact:** A medical director reading "48% to 26% reduction from dashboard plus education" would: (1) expect near-halving of prescribing from a two-component intervention, when the actual immediate effect was a reduction to 33%; (2) not know that financial incentives were part of the package, which is essential for replication; (3) set unrealistic expectations for timeline and effort.

**Full verification report:** [citation8_verification.md](verification/citation8_verification.md)

---

### Citation 9: Gerber et al., JAMA, 2013

> Gerber JS, Prasad PA, Fiks AG, et al. Effect of an Outpatient Antimicrobial Stewardship Intervention on Broad-Spectrum Antibiotic Prescribing by Primary Care Pediatricians: A Randomized Trial. *JAMA*. 2013;309(22):2345-52. doi:10.1001/jama.2013.6287.

| Phase | Result |
|-------|--------|
| Phase 0 | DOI exists in CrossRef |
| Phase 1 | Resolves to JAMA (PMID 23757082) |
| Phase 2 | **N/A: No inline claim cites [9]** |
| Phase 3 | All metadata correct |

**Error detail:**

Citation [9] has no corresponding inline claim in the OpenEvidence response. Citations [1] through [8] each support at least one specific assertion in the response text. Citation [9] appears only in the reference list or supplementary section.

The paper itself is a landmark cluster-randomized trial of outpatient antibiotic stewardship in 18 pediatric primary care practices (CHOP network, Pennsylvania/New Jersey). It demonstrated that a 1-hour education session plus quarterly personalized audit-and-feedback reduced broad-spectrum antibiotic prescribing from 26.8% to 14.3% in intervention practices (vs. 28.4% to 22.6% in controls; difference-in-differences: 6.7 pp, P = .01).

**Critical distinction:** The study measured **broad-spectrum** antibiotic prescribing (shifting from broad-spectrum to narrow-spectrum agents), not total antibiotic prescribing. It aimed to improve antibiotic choice, not reduce overall prescribing. The OpenEvidence response discusses total prescribing reduction, which is a different outcome.

**Error classification:** DECORATION_CITATION

Decoration citations create the appearance of thorough sourcing without the substance. A physician reviewing the reference list would see "JAMA, 2013, randomized trial" and reasonably assume the response draws on its findings. It does not. The citation exists to signal rigor, not to provide evidence for any specific claim.

Severity is low (no incorrect claim is made; the paper is real and topically relevant), but the pattern matters at scale: if 1-2 of 9 citations are decorative, the response appears more thoroughly sourced than it actually is.

**Full verification report:** [citation9_verification.md](verification/citation9_verification.md)

---

## Error Pattern Analysis

### Complete Failure Mode Inventory

| # | Error Category | Citations Affected | Pipeline Phase | Severity |
|---|----------------|-------------------|----------------|----------|
| 1 | Claim-citation misattribution (cross-paper swap) | 2 | Phase 2 | High |
| 2 | Citation overloading (multiple studies collapsed into one citation) | 4 | Phase 2 | Moderate |
| 3 | Intervention misattribution (85% figure attributed to wrong intervention) | 4 | Phase 2 | High |
| 4 | Intervention mischaracterization (retrospective dashboard described as real-time CDS) | 7 | Phase 2 | High |
| 5 | Statistic conflation (two study periods collapsed into one figure) | 8 | Phase 2 | High |
| 6 | Intervention simplification (4 components reduced to 2) | 8 | Phase 2 | Moderate |
| 7 | Financial incentive omission (compensation-linked quality metrics unreported) | 8 | Phase 2 | High |
| 8 | Denominator shift (population-level stat reframed as reporter-level) | 1 | Phase 2 | Moderate |
| 9 | Qualifier omission ("rare" dropped from rheumatic fever) | 1 | Phase 2 | Low |
| 10 | Drawback omission (delayed prescribing trade-offs suppressed) | 1 | Phase 2 | Moderate |
| 11 | Ambiguous data presentation (treatment duration vs. illness duration) | 1 | Phase 2 | Low |
| 12 | Decoration citation (reference list padding with no inline claim) | 9 | Phase 2 | Low |

Every error is a Phase 2 finding. Phases 0, 1, and 3 returned clean results across all 9 citations. This confirms the core finding of the Citation Verification Pipeline: the errors that matter most are invisible to automated checking.

### Patterns Observed

**1. Claim-citation misattribution (Citation 2).** Real statistics from the broader antibiotic stewardship literature are bundled under whichever citation happens to be nearby. The 60% (sore throat) and 71% (bronchitis) prescribing rates exist in published research (Barnett & Linder, 2014), but OpenEvidence attributes them to a Spanish RCT that never reported those figures.

**2. Citation overloading (Citation 4).** A single guideline paper (Harris et al. 2016) is used as the citation for findings from at least four separate research programs. This makes the citation look well-sourced while obscuring that the actual evidence comes from different research teams with different methodologies.

**3. Intervention misattribution (Citation 4).** The "85% decrease in antibiotic prescribing" is a real finding from Mangione-Smith et al. 2015 (combined provider communication strategies), correctly cited in Harris et al. 2016. OpenEvidence attributes this figure to "labeling bronchitis as 'chest cold,'" which is a different intervention entirely (Phillips & Hickner 2005, which measured patient satisfaction, not prescribing rates). The clinical consequence: a provider implementing "chest cold" labeling would expect an 85% prescribing reduction that this strategy alone has never demonstrated.

**4. Intervention mischaracterization (Citation 7).** A retrospective prescribing dashboard (Microsoft Power BI, updated monthly, separate from EHR) is described as "electronic decision support systems," implying real-time CDS functionality. This matters because CDS infrastructure and retrospective dashboards have different implementation costs, workflow implications, and evidence bases.

**5. Compound misrepresentation (Citation 8).** Three distinct errors in one claim: temporal conflation (collapsing 3-year trajectory into one figure), intervention simplification (4 components to 2), and financial incentive omission (compensation-linked quality metrics). Each error alone would be noteworthy; together they substantially distort what this study demonstrated and what it takes to replicate.

**6. Selective presentation (Citation 1).** Four subtle reframing errors in a citation otherwise classified as "clean": denominator shift on penicillin allergy, omission of delayed prescribing drawbacks, dropping the "rare" qualifier from rheumatic fever, and ambiguous presentation of treatment durations. None are fabrications, but collectively they demonstrate a pattern of presenting findings in the most favorable light while suppressing caveats.

**7. Decoration citation (Citation 9).** A landmark JAMA RCT included in the reference list without supporting any inline claim. This inflates perceived rigor without adding evidentiary substance.

### Error Severity Distribution

| Severity | Count | Examples |
|----------|-------|---------|
| High | 5 | Cross-paper swap, 85% misattribution, CDS mischaracterization, temporal conflation, financial incentive omission |
| Moderate | 4 | Citation overloading, intervention simplification, denominator shift, drawback omission |
| Low | 3 | Qualifier omission, ambiguous presentation, decoration citation |

### What Standard Verification Misses

| Verification Method | Errors Detected | Errors Missed |
|--------------------|-----------------|---------------|
| URL/link checking (Phase 0-1 only) | 0/12 | 12/12 (100% miss rate) |
| URL + metadata checking (Phase 0-1-3) | 0/12 | 12/12 (100% miss rate) |
| Full pipeline including content verification (Phase 0-4) | 12/12 | 0/12 |

A standard citation audit checking URL resolution, DOI validity, and metadata accuracy would have returned a **perfect score** for this OpenEvidence response. Every error requires reading the cited paper and comparing its actual findings to the inline claim.

---

## Audit Self-Correction

The second pass identified one false positive in the original audit:

| Item | Original Classification | Corrected Classification | Reason |
|------|------------------------|-------------------------|--------|
| "First-line agents for otitis media" attributed to [4] | Misattributed | **FALSE POSITIVE (removed)** | Three independent reviews of the OpenEvidence response confirmed otitis media is mentioned only once, attributed to [1], not [4] |

This demonstrates that the audit methodology is self-correcting: the second pass catches errors in the first pass, including our own audit's errors.

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

1. **Detect misattributed statistics:** Flag when a specific percentage (60%, 71%, 85%) appears in the response text but not in the cited paper's abstract or findings
2. **Detect statistic conflation:** Flag when a cited figure spans two different study periods or populations without explicit qualification
3. **Detect intervention mischaracterization:** Flag when the description of an intervention (e.g., "electronic decision support") does not match the intervention type documented in the cited paper's methods section
4. **Detect citation overloading:** Flag when a single citation is used to support more than 3-4 distinct claims, indicating that multiple source papers may be collapsed into one citation
5. **Detect decoration citations:** Flag citations that appear in the reference list but are not used to support any inline claim
6. **Detect denominator shifts:** Flag when a statistic's denominator in the response differs from the denominator in the source paper
7. **Detect selective omission:** Flag when the response presents a finding without documented trade-offs, caveats, or qualifiers that appear in the source paper

### The Verification Gap as a Product Risk

The PMC-indexed paper "OpenEvidence: Enhancing Medical Student Clinical Rotations With AI but With Limitations" (January 2025) already documents citation hallucination as a limitation. The findings in this audit confirm that the vulnerability extends beyond fabricated citations to a subtler category: accurate citations with inaccurate claim-citation alignment.

This category is harder to detect, harder to prevent, and harder to explain to users. A physician who clicks a JAMA Network Open citation and finds the paper exists may assume the attributed finding is correct. They would need to read the full paper and compare its specific data to the AI's claim to discover the discrepancy.

---

## Appendix A: Citation Status Summary

| # | Citation | Phase 0-1 | Phase 2 | Phase 3 | Failure Modes |
|---|----------|-----------|---------|---------|---------------|
| 1 | Sur & Plesa, AFP 2022 | Pass | 4 subtle issues | Pass | Denominator shift, drawback omission, qualifier omission, ambiguity |
| 2 | de la Poza Abad et al., JAMA IM 2016 | Pass | **Fail** | Pass | Cross-paper citation swap |
| 3 | Kuijpers et al., Lancet ID 2025 | Pass | Pass | Pass | Clean (minor scope caveat) |
| 4 | Harris et al., Ann Intern Med 2016 | Pass | **Fail** | Pass | Citation overloading, intervention misattribution (85%), peer comparison misattribution |
| 5 | Libman et al., Ann Intern Med 2017 | Pass | Pass | Pass | Clean (secondary source) |
| 6 | File & Ramirez, NEJM 2023 | Pass | Pass | Pass | Clean (clinical completeness caveat) |
| 7 | Davidson et al., ICHE 2023 | Pass | **Fail** | Pass | Intervention mischaracterization |
| 8 | Stenehjem et al., JAMA NO 2023 | Pass | **Fail** | Pass | Temporal conflation, intervention simplification, financial incentive omission |
| 9 | Gerber et al., JAMA 2013 | Pass | N/A | Pass | Decoration citation (no inline claim) |

## Appendix B: Verification Reports

Individual verification reports for each citation are available in the [verification/](verification/) directory:

- [citation1_verification.md](verification/citation1_verification.md) - Sur & Plesa, AFP 2022
- [citation2_verification.md](verification/citation2_verification.md) - de la Poza Abad et al., JAMA IM 2016
- [citation3_verification.md](verification/citation3_verification.md) - Kuijpers et al., Lancet ID 2025
- [citation4_verification.md](verification/citation4_verification.md) - Harris et al., Ann Intern Med 2016
- [citation5_verification.md](verification/citation5_verification.md) - Libman et al., Ann Intern Med 2017
- [citation6_verification.md](verification/citation6_verification.md) - File & Ramirez, NEJM 2023
- [citation7_verification.md](verification/citation7_verification.md) - Davidson et al., ICHE 2023
- [citation8_verification.md](verification/citation8_verification.md) - Stenehjem et al., JAMA NO 2023
- [citation9_verification.md](verification/citation9_verification.md) - Gerber et al., JAMA 2013

## Appendix C: Methodology Reference

This audit was conducted using the Five-Phase Citation Verification Pipeline documented in `METHODOLOGY.md`. The pipeline, error taxonomy, and defense architecture are available at:

**Repository:** [citation-hallucination-audit](https://github.com/BryanTegomoh/citation-hallucination-audit)

The pipeline was developed through systematic verification of 150+ citations across 22 medical specialty chapters, identifying 21 distinct failure modes (Gaps 1-21) documented in the methodology. This OpenEvidence audit demonstrates the pipeline's application to clinical AI platform outputs, confirming that content-level verification (Phase 2) is the critical layer for systems that have already solved URL-level accuracy.

---

*Audit conducted March 4, 2026. All verification searches executed in real time against PubMed, CrossRef, and publisher websites. Second-pass comprehensive re-verification completed same day.*
