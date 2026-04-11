# Citation 8 Verification Report

**Verification date:** 2026-03-04
**Auditor:** Bryan Tegomoh

---

## Citation Under Review

**OpenEvidence citation:**
> Stenehjem E, Wallin A, Willis P, et al. Implementation of an Antibiotic Stewardship Initiative in a Large Urgent Care Network. JAMA Network Open. 2023;6(5):e2313011. doi:10.1001/jamanetworkopen.2023.13011.

**Claim attributed to [8]:**
> "A large urgent care network demonstrated sustained reductions in antibiotic prescribing from 48% to 26% using dashboard feedback combined with education"

---

## 1. Metadata Verification

| Field | OpenEvidence Citation | Verified Value | Match? |
|-------|----------------------|----------------|--------|
| First author | Stenehjem E | Stenehjem E (Edward Stenehjem, Intermountain Health) | YES |
| Co-authors | Wallin A, Willis P, et al. | Wallin A, Willis P, Kumar N, Seibert AM, Buckel WR, Stanfield V, Brunisholz KD, Fino N, Samore MH, Srivastava R, Hicks LA, Hersh AL | YES |
| Title | Implementation of an Antibiotic Stewardship Initiative in a Large Urgent Care Network | Exact match | YES |
| Journal | JAMA Network Open | JAMA Network Open | YES |
| Year | 2023 | Published May 1, 2023 | YES |
| Volume/Issue | 6(5) | 6(5) | YES |
| Article ID | e2313011 | e2313011 | YES |
| DOI | 10.1001/jamanetworkopen.2023.13011 | Resolves correctly (302 redirect to jamanetwork.com/journals/jamanetworkopen/fullarticle/2804780) | YES |
| PMID | Not provided by OpenEvidence | 37166794 (confirmed) | N/A |
| PMCID | Not provided by OpenEvidence | PMC10176123 (open access full text) | N/A |

**Metadata verdict: All metadata fields are accurate.**

---

## 2. Prescribing Rate Verification

### Actual rates from the paper (Table 1 and Results):

| Period | Dates | Antibiotic Prescribing Rate | Encounters |
|--------|-------|-----------------------------|------------|
| Baseline | July 1, 2018 - June 30, 2019 | **47.8%** | 493,724 |
| Intervention | July 1, 2019 - June 30, 2020 | **33.3%** | 471,136 |
| Sustainability | July 1, 2020 - June 30, 2021 | **25.5%** | 391,608 |

### OpenEvidence claim: "from 48% to 26%"

- **"48%" (baseline):** Approximately correct. The actual figure is 47.8%, which rounds to 48%. Intermountain Health's own press release also uses "48%." This is acceptable rounding. **ACCURATE.**

- **"26%" (endpoint):** This is where the problem lies. No single time point in the study shows exactly 26%.
  - The intervention period endpoint was **33.3%** (not 26%)
  - The sustainability period endpoint was **25.5%** (closest to 26%, but this is a different period)
  - OpenEvidence appears to have rounded 25.5% up to 26%, which is itself a minor rounding issue, but the real problem is that "48% to 26%" conflates two different study phases

### What actually happened:

```
Baseline (47.8%) --[intervention]--> 33.3% --[sustainability]--> 25.5%
                    14.5 pp drop              7.8 pp further drop
```

The reduction from 47.8% to 25.5% spans the ENTIRE study (baseline through sustainability, a full 3 years). It was NOT a single intervention producing a direct 48%-to-26% reduction. The claim collapses a two-phase trajectory into one.

---

## 3. Claim Accuracy Assessment

### OpenEvidence claim decomposition:

| Claim Element | Accurate? | Actual Finding |
|---------------|-----------|----------------|
| "A large urgent care network" | YES | 38-39 Intermountain Health urgent care clinics across Utah |
| "sustained reductions" | PARTIALLY | Reductions were sustained, but the 25.5% figure is from the *sustainability* period, not the intervention period itself |
| "from 48% to 26%" | MISLEADING | Baseline was 47.8% (rounds to 48%), but the intervention reduced prescribing to 33.3%, not 26%. The 25.5% rate (rounded to 26%) was achieved during the subsequent sustainability period |
| "using dashboard feedback combined with education" | INCOMPLETE | The intervention had FOUR components, not two. Additionally, a financial incentive was introduced that the claim omits entirely |

---

## 4. Intervention Components: What OpenEvidence Omitted

### Actual intervention (four domains based on CDC Core Elements of Outpatient Antibiotic Stewardship):

1. **Education** for clinicians (peer training, handbooks, podcasts) and patients (materials)
2. **EHR tools** (clinical decision support alerts, delayed prescription options, templated notes)
3. **Transparent clinician benchmarking dashboard** with peer comparison
4. **Media outreach** (television, radio, social media, in-clinic signage targeting clinicians and patients)

### The financial incentive OpenEvidence completely omitted:

Urgent care leadership independently introduced a **financial incentive** tied to clinician compensation: clinicians who prescribed antibiotics in fewer than 50% of respiratory encounters received increased compensation eligibility. The paper explicitly acknowledges this as a limitation because "the impact of stewardship intervention and quality measures linked to provider compensation could not be evaluated independently."

**This is a critical omission.** Describing the intervention as "dashboard feedback combined with education" strips out the EHR tools, mass media campaign, AND financial incentive, all of which could have contributed meaningfully to the observed reductions. The financial incentive is especially significant because it represents an entirely different mechanism of behavior change (extrinsic motivation) compared to education and feedback (intrinsic motivation/awareness).

---

## 5. Study Design

- **Design:** Interrupted time series analysis (quality improvement study, not an RCT)
- **Statistical method:** Binomial generalized estimating equations comparing pre-post periods
- **Setting:** 38-39 Intermountain Health urgent care clinics (32 all-ages, 6 pediatric-only) in Utah
- **COVID-19 overlap:** The final 3 months of the intervention period (April-June 2020) overlapped with COVID-19 onset. The sustainability period (July 2020 - June 2021) occurred entirely during the pandemic. Sensitivity analyses found COVID-19 did not significantly alter primary findings, but the pandemic likely reduced respiratory visits and may have influenced prescribing patterns.

---

## 6. Error Classification

### Error Type: Compound misrepresentation (multiple simultaneous inaccuracies)

| Error Category | Severity | Description |
|----------------|----------|-------------|
| **Temporal conflation** | MODERATE | Collapsing a 3-year, two-phase trajectory (baseline to sustainability) into a single "from X to Y" reduction, implying a direct intervention effect |
| **Intervention simplification** | HIGH | Reducing a 4-component intervention plus financial incentive to "dashboard feedback combined with education" |
| **Financial incentive omission** | HIGH | Complete omission of compensation-linked quality measure, which the paper itself flags as a confounding limitation |
| **Numeric rounding** | LOW | 47.8% to 48% is acceptable; 25.5% to 26% is acceptable in isolation but compounds the temporal conflation problem |

### Overall severity: HIGH

The claim is not fabricated (the paper exists, the numbers are in the right ballpark), but it misrepresents the study in ways that could mislead clinical or policy decision-making:

1. A reader would conclude that dashboard feedback plus education alone produced a 22-percentage-point reduction, when in fact the actual intervention-period reduction was 14.5 pp (to 33.3%), with further reductions occurring during a separate sustainability period
2. A reader would not know that financial incentives were part of the package, which is essential for anyone trying to replicate this program
3. The omission of EHR tools and media campaigns understates implementation complexity

---

## 7. What the Correct Summary Should Say

A more accurate representation of this study:

> An Intermountain Health quality improvement initiative across 38-39 urgent care clinics implemented a multifaceted antibiotic stewardship program including clinician education, EHR decision support tools, transparent benchmarking dashboards, media campaigns, and a financial incentive linking prescribing rates to clinician compensation. Antibiotic prescribing for respiratory conditions decreased from 47.8% at baseline to 33.3% during the one-year intervention period, with further reductions to 25.5% during the subsequent sustainability year. The independent contribution of each component, including the financial incentive, could not be separated (Stenehjem et al., 2023).

---

## 8. Verification Sources

- PubMed: https://pubmed.ncbi.nlm.nih.gov/37166794/
- PMC full text: https://pmc.ncbi.nlm.nih.gov/articles/PMC10176123/
- JAMA Network Open: https://jamanetwork.com/journals/jamanetworkopen/fullarticle/2804780
- DOI: https://doi.org/10.1001/jamanetworkopen.2023.13011
- CIDRAP coverage: https://www.cidrap.umn.edu/antimicrobial-stewardship/study-highlights-highly-successful-urgent-care-stewardship-intervention
- SHEA Journal Club: https://shea-online.org/shea-journal-club/june-2023/antimicrobial-stewardship-in-urgent-care-works/
- Intermountain Health press release: https://news.intermountainhealth.org/new-utah-study-finds-antibiotic-stewardship-program-significantly-reduced-prescribing-rates-of-antibiotics-at-urgent-care-centers-in-promising-initiative-to-curb-antibiotic-overuse/
