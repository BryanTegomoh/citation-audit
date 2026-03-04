# Citation 7 Verification Report

**Citation under review:**
Davidson LE, Gentry EM, Priem JS, Kowalkowski M, Spencer MD. A Multimodal Intervention to Decrease Inappropriate Outpatient Antibiotic Prescribing for Upper Respiratory Tract Infections in a Large Integrated Healthcare System. *Infection Control and Hospital Epidemiology*. 2023;44(3):392-399. doi:10.1017/ice.2022.83.

**Audit context:** OpenEvidence response on antibiotic stewardship strategies in outpatient respiratory infections
**Date verified:** March 4, 2026

---

## 1. Paper Existence and PMID Verification

**PMID 35491941: CONFIRMED.**

The paper exists at [PubMed](https://pubmed.ncbi.nlm.nih.gov/35491941/) and at [Cambridge Core](https://www.cambridge.org/core/journals/infection-control-and-hospital-epidemiology/article/multimodal-intervention-to-decrease-inappropriate-outpatient-antibiotic-prescribing-for-upper-respiratory-tract-infections-in-a-large-integrated-healthcare-system/62DE08C556CE63F44E42538C82064251). The DOI (10.1017/ice.2022.83) resolves via CrossRef to the correct *Infection Control & Hospital Epidemiology* article page. The DOI prefix 10.1017 correctly corresponds to Cambridge University Press.

---

## 2. Publication Date: Online vs. Print

**This is a critical metadata detail.**

| Date Type | Date |
|-----------|------|
| Epub (online first) | **May 2, 2022** |
| Print issue | **March 2023** (Volume 44, Issue 3) |

The PMID 35491941 was assigned in May 2022 when the article was published online. The paper appeared in print in the March 2023 issue. The OpenEvidence citation lists "2023" as the year, which is the print publication year. Both "2022" (epub) and "2023" (print) are defensible depending on citation convention. PubMed displays both dates. The 9-month gap between online and print publication is typical for journals with publication queues.

**Verdict:** The "2023" year in the citation is correct for the print volume/issue assignment. A citation using "2022" (epub date) would also be valid. This is not an error.

---

## 3. The CHOSEN Program: What Was the Actual Intervention?

The intervention was the **Carolinas Healthcare Outpatient Antimicrobial Stewardship Empowerment Network (CHOSEN)**, a multicomponent outpatient stewardship program at Atrium Health (formerly Carolinas HealthCare System) in the greater Charlotte, North Carolina region.

### All Intervention Components Identified

Based on the PubMed abstract, the IDWeek 2018 conference abstracts (PMC6252619, PMC6252853), and the ASHP coverage, the CHOSEN program included:

| Component | Description | Source |
|-----------|-------------|--------|
| **Web-based provider prescribing dashboard** | Built in Microsoft Power BI. Retrospective analytics tool displaying historical prescribing rates by indication, antibiotic agent, practice site, and specialty. Updated monthly. | IDWeek abstract (PMC6252619); PubMed abstract |
| **Provider educational materials** | Scripting templates for clinicians; on-site education sessions targeting urgent care, family medicine, internal medicine, and pediatrics. | IDWeek abstract (PMC6252853); PubMed abstract |
| **Patient educational materials** | "Bacteria and Viruses" handout with symptom checklists, separate guides for adults/teens/children translated into 11 languages, patient commitment flyer for exam rooms, pediatric dosing guides for acetaminophen/ibuprofen, two educational videos. | IDWeek abstract (PMC6252853) |
| **Targeted on-site education** | Practice leaders received education on dashboard usage with "tips to address high prescribing." Monthly data updates enabled targeted on-site education for highest-prescribing groups. | IDWeek abstract (PMC6252619) |
| **Consumer/public outreach** | Consumer webpage, provider intranet updates, media outreach featuring community providers. Coordinated with CDC's National Antibiotic Awareness Week (November 2017). | IDWeek abstract (PMC6252853) |

### What the Intervention Was NOT

| NOT This | Explanation |
|----------|-------------|
| Real-time electronic clinical decision support (CDS) | No best practice alerts, no point-of-care prompts, no EHR-embedded alerts during patient encounters |
| Financial incentives | No evidence of quality metrics tied to compensation or financial consequences for prescribing behavior |
| Justification alerts | No requirement for clinicians to enter a rationale before prescribing antibiotics |
| Commitment posters (Meeker-style) | Patient commitment flyers existed for exam rooms, but these are patient-facing educational materials, not the public clinician commitment intervention studied by Meeker et al. 2016 |

---

## 4. The Dashboard: Retrospective Feedback, Not Real-Time CDS

This distinction is central to the audit finding.

**The CHOSEN dashboard was a retrospective prescribing analytics tool:**
- Built on Microsoft Power BI (a business intelligence platform)
- Displayed historical prescribing data, not real-time guidance
- Updated monthly (not during patient encounters)
- Accessed as a separate web-based tool, not embedded in the EHR workflow
- Allowed drill-down to practice-level and provider-level data
- Showed prescribing rates alongside evidence-based specialty-specific target rates (ranging from 38.7% to 47.2% depending on specialty)

**"Electronic decision support systems" implies:**
- Real-time alerts during the clinical encounter
- Point-of-care prompts within the EHR
- Interruption-based workflow (e.g., best practice alerts firing when an antibiotic is ordered)
- Automated suggestions at the moment of prescribing

These are fundamentally different intervention types with different implementation costs, different workflow implications, and different evidence bases.

---

## 5. Peer Comparison: Present, But Nuanced

**Does the CHOSEN dashboard include peer comparison?**

**Yes, but it is implicit rather than explicit benchmarking.**

The ASHP coverage (January 2019) quotes the investigators describing the dashboard as allowing users to "look at their own prescribing rates and patterns, compare them to those of their peers, and see where they're having success and where they may need to have to pay more attention to details."

The IDWeek abstract (PMC6252619) describes specialty-specific target rates and the ability to view data at practice and provider levels, which enables comparison but is distinct from the Meeker et al. (2016) model of explicit peer comparison reporting (where providers receive personalized letters ranking them against top performers with social pressure framing).

**Distinction:**

| Feature | CHOSEN Dashboard | Meeker et al. 2016 Peer Comparison |
|---------|-----------------|-------------------------------------|
| Data access | Self-service drill-down | Personalized letter/report sent to provider |
| Comparison type | Implicit (view own rates alongside targets and other sites) | Explicit (ranked against "top performers" with social norm messaging) |
| Frequency | Monthly updates, self-accessed | Periodic individual reports delivered |
| Social pressure | Low (voluntary comparison) | High (direct ranking with peer norms) |
| Behavioral mechanism | Awareness/accountability | Social norm conformity |

**Assessment:** The OpenEvidence claim that [7] demonstrates "audit and feedback mechanisms, including provider prescribing dashboards with peer comparison" is partially supported. The CHOSEN dashboard does enable peer comparison, but it is a voluntary analytics tool, not the structured audit-and-feedback-with-social-norms intervention that "peer comparison" typically denotes in the antibiotic stewardship literature (which traces to Meeker et al. 2016, JAMA).

---

## 6. The 16.6-20.4% Reduction: Verification

**CONFIRMED. The range is accurately reported.**

The abstract reports reductions in inappropriate prescribing rates (percentage of encounters with inappropriate antibiotic prescribing) across specialties:

| Specialty | Reduction in Inappropriate Prescribing Rate |
|-----------|---------------------------------------------|
| Family medicine | -20.4% |
| Internal medicine | -19.5% |
| Pediatric medicine | -17.2% |
| Urgent care | -16.6% |

The 16.6-20.4% range correctly spans the lowest (urgent care) to highest (family medicine) specialty-specific reductions. These are absolute reductions in the inappropriate prescribing rate, not relative reductions.

**What was measured:** The study measured *inappropriate* antibiotic prescribing rates for upper respiratory tract infections. This is not total antibiotic prescribing; it is specifically the rate of prescribing considered inappropriate for the diagnosis.

**Study design:** Before-and-after interrupted time series comparing two periods:
- Pre-intervention: April 2016 to October 2017
- Post-intervention: May 2018 to March 2020
- Setting: 162 primary care practices in a large healthcare system

---

## 7. Financial Incentives

**No evidence of financial incentives in the CHOSEN program.**

Multiple searches for "financial incentive," "value-based," "quality metric," and "compensation" in connection with the CHOSEN program returned no results. The PubMed abstract does not mention financial incentives. The IDWeek conference abstracts do not mention them. The ASHP coverage does not mention them.

This is a relevant distinction because the Stenehjem et al. 2023 study (Citation [8] in the same OpenEvidence response) *did* include financial incentives as part of its intervention. Conflating the two studies' intervention components would misrepresent what drove the results in each case.

---

## 8. Claim-by-Claim Verification Against OpenEvidence

### Claim 1: "Electronic decision support systems and provider dashboards have demonstrated significant reductions in inappropriate prescribing" [7]

**Verdict: INTERVENTION MISCHARACTERIZED.**

| Element | OpenEvidence Claim | Actual Paper |
|---------|-------------------|--------------|
| Intervention type | "Electronic decision support systems" | Retrospective web-based prescribing dashboard (Microsoft Power BI) |
| Nature of tool | Implies real-time CDS in EHR | Monthly retrospective analytics, separate from EHR |
| Dashboard mentioned | Yes ("provider dashboards") | Confirmed |
| Reductions demonstrated | Yes ("significant reductions") | Confirmed (16.6-20.4% across specialties) |

The claim bundles "electronic decision support systems" and "provider dashboards" as if they were both present in this study. Only the dashboard component is accurate. The study did not implement electronic decision support systems.

**Error classification:** CLAIM_MISMATCH (intervention type mischaracterized). The term "electronic decision support systems" implies a different category of technology (real-time, EHR-integrated, point-of-care) than what was actually studied (retrospective, web-based, reviewed after encounters).

---

### Claim 2: "multimodal intervention in a large healthcare system reduced inappropriate prescribing by 16.6-20.4%" [7]

**Verdict: CONFIRMED.**

- "Multimodal intervention": Accurate. The CHOSEN program had multiple components (dashboard, provider education, patient education, on-site training, public outreach).
- "Large healthcare system": Accurate. Atrium Health, 162 primary care practices, approximately 1,060,000 patients.
- "Reduced inappropriate prescribing by 16.6-20.4%": Accurate. These figures match the abstract's specialty-specific reductions.
- The range represents variation by specialty (urgent care at the low end, family medicine at the high end), which is not specified in the OpenEvidence text but is an acceptable summary.

---

### Claim 3: "Audit and feedback mechanisms, including provider prescribing dashboards with peer comparison" [4] and [7]

**Verdict: PARTIALLY SUPPORTED with significant caveats.**

| Element | Assessment |
|---------|------------|
| "Provider prescribing dashboards" | CONFIRMED. The CHOSEN dashboard is a prescribing analytics dashboard. |
| "Peer comparison" | PARTIALLY SUPPORTED. The dashboard enables implicit comparison (viewing own rates alongside peers, practices, and targets). However, this is voluntary self-service analytics, not the structured peer comparison reporting (individualized letters with ranking and social norms) typically denoted by "peer comparison" in the stewardship literature. |
| "Audit and feedback mechanisms" | PARTIALLY SUPPORTED. The dashboard provides feedback on prescribing patterns, and targeted on-site education was triggered by high-prescribing data. However, "audit and feedback" in the stewardship literature typically refers to structured periodic reports sent to individual providers (the Gerber et al. 2013 model), not a self-accessed dashboard. |

The CHOSEN dashboard has elements of audit/feedback and peer comparison, but it is a lighter-touch intervention than what those terms conventionally describe. The OpenEvidence phrasing implies a more structured, individualized intervention than what was actually implemented.

---

## 9. Additional Findings

### Study Also Measured First-Line Antibiotic Selection and Duration

Beyond inappropriate prescribing rates, the study found:
- Higher percentage of first-line antibiotic prescribing in intervention clinics: 83.1% vs. 77.7% (P = 0.024)
- Shorter antibiotic duration in intervention clinics: 9.28 +/- 1.56 days vs. 9.79 +/- 0.75 days (P < 0.001)

These findings are not mentioned in the OpenEvidence response but represent additional positive outcomes of the CHOSEN intervention.

### Scale of the Program

The CHOSEN program is notable for its scale:
- 162 primary care practices across metropolitan, suburban, and rural communities
- Approximately 1,060,000 patients
- Developed through stakeholder-centered design involving physicians, nurses, pharmacists, quality specialists, marketing professionals, and patient experience representatives
- Patient materials translated into 11 languages
- Baseline research included 190 patient surveys and stakeholder interviews

---

## Summary Verdict

| Phase | Result |
|-------|--------|
| Phase 0 (DOI exists) | PASS: DOI 10.1017/ice.2022.83 exists in CrossRef, resolves correctly |
| Phase 1 (URL resolves) | PASS: PubMed and Cambridge Core both accessible |
| Phase 2 (claims supported) | **MIXED: Statistics confirmed; intervention type mischaracterized** |
| Phase 3 (metadata correct) | PASS: All fields verified against PubMed |
| Phase 4 (correction) | Intervention was CHOSEN dashboard + education, not "electronic decision support systems" |

### Error Summary

| Claim | Status | Error Type |
|-------|--------|------------|
| "Electronic decision support systems" | **MISCHARACTERIZED** | CLAIM_MISMATCH: retrospective dashboard described as real-time CDS |
| "16.6-20.4% reduction" | CONFIRMED | Accurate |
| "Provider dashboards" | CONFIRMED | Accurate |
| "Peer comparison" | PARTIALLY SUPPORTED | Dashboard enables implicit comparison; not structured peer comparison reporting |
| "Audit and feedback" | PARTIALLY SUPPORTED | Dashboard provides data for feedback; not structured audit-and-feedback per conventional definition |
| Financial incentives | NOT PRESENT | The CHOSEN program did not include financial incentives |

### Clinical Impact of the Mischaracterization

The "electronic decision support systems" label matters for implementation decisions:

1. **Resource allocation:** Real-time CDS requires EHR integration, IT development, clinical informaticist involvement, alert fatigue management, and ongoing maintenance. A retrospective Power BI dashboard requires data extraction, visualization design, and distribution, with substantially lower cost and complexity.

2. **Evidence mapping:** A health system reading the OpenEvidence response and attributing the 16.6-20.4% reduction to "electronic decision support" might invest in CDS infrastructure. The evidence actually supports a simpler approach: a retrospective dashboard combined with education.

3. **Intervention design:** The CHOSEN model's success came from making prescribing data transparent and accessible, combined with education and on-site coaching for high prescribers. This is a behavioral/informational intervention, not a technology-interruption intervention.

---

## Sources Consulted

- [PubMed Record (PMID 35491941)](https://pubmed.ncbi.nlm.nih.gov/35491941/)
- [Cambridge Core Article Page](https://www.cambridge.org/core/journals/infection-control-and-hospital-epidemiology/article/multimodal-intervention-to-decrease-inappropriate-outpatient-antibiotic-prescribing-for-upper-respiratory-tract-infections-in-a-large-integrated-healthcare-system/62DE08C556CE63F44E42538C82064251)
- [IDWeek 2018 Abstract: Dashboard Development (PMC6252619)](https://pmc.ncbi.nlm.nih.gov/articles/PMC6252619/)
- [IDWeek 2018 Abstract: Patient/Provider Education (PMC6252853)](https://pmc.ncbi.nlm.nih.gov/articles/PMC6252853/)
- [ASHP News: Novel Tool Supports Appropriate Outpatient Antimicrobial Use (January 2019)](https://news.ashp.org/news/ashp-news/2019/01/03/novel-tool-supports-appropriate-outpatient-antimicrobial-use)

---

*Verification conducted March 4, 2026 using the Five-Phase Citation Verification Pipeline.*
