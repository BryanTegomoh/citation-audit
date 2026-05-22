# Clinical Evidence Grounding Framework

## Purpose

Cited clinical AI systems should be evaluated at the level where clinicians rely on them: the individual claim. A reference can be real, correctly formatted, and topically relevant while still failing to support the exact statistic, guideline threshold, intervention, population, or conclusion attached to it.

This framework defines a practical evaluation layer for medical AI products that provide sourced answers at the point of care. It is designed to sit beside retrieval, model evaluation, and clinical review without slowing product teams or requiring access to internal model weights.

## Policy Standard

A cited answer is not grounded until the following units match between the answer and the source:

| Unit | Required Check |
|------|----------------|
| Claim | The cited source directly supports the sentence or clause attached to it |
| Population | Age, disease state, geography, care setting, and risk group match |
| Intervention | Drug, dose, procedure, diagnostic test, or workflow matches |
| Comparator | Control arm, alternative therapy, or baseline condition matches |
| Outcome | The cited endpoint is the endpoint reported in the source |
| Statistic | Numerator, denominator, time horizon, and estimand match |
| Guideline context | Organization, jurisdiction, year, and recommendation class match |
| Evidence strength | Language matches study design and certainty of evidence |

The minimum product standard is simple: every high-impact clinical claim must have a source-linked support judgment before it is treated as verified.

## Evaluation Layers

### 1. Structural Verification

These checks confirm that the reference is real:

- DOI or URL resolves
- PubMed, CrossRef, or publisher metadata match the citation
- First author, year, journal, and title are correct
- Retraction or major correction status is checked

Structural verification is necessary but not sufficient. It catches broken references, not unsupported synthesis.

### 2. Claim-Level Grounding

Each cited answer is decomposed into atomic claims. A reviewer or evaluator assigns one of four labels:

| Label | Meaning |
|-------|---------|
| Supported | Source directly supports the claim as written |
| Partially supported | Source supports the broad idea but not the exact wording, scope, or number |
| Unsupported | Source is real but does not support the claim |
| Not assessable | Source access, paywall, or answer ambiguity prevents judgment |

Every unsupported or partially supported claim is also assigned a failure mode and severity.

### 3. Clinical Severity

Severity is based on how the error could affect clinical reasoning:

| Severity | Meaning |
|----------|---------|
| High | Could change diagnosis, treatment, triage, dosing, contraindication handling, or reimbursement decision |
| Medium | Could mislead implementation, evidence interpretation, or counseling |
| Low | Primarily affects precision, attribution, or perceived evidence strength |

This keeps the evaluation product-focused. The goal is not to punish harmless citation imperfections. The goal is to find errors that matter in clinical use.

## Core Failure Modes

The highest-yield eval set should emphasize failures that pass ordinary citation checks:

| Failure Mode | Product Risk |
|--------------|--------------|
| Denominator shift | Same number, different population or denominator |
| Trial identity mismatch | Statistic from one trial attributed to another |
| Cross-paper statistical conflation | Figures from multiple papers assembled into one claim |
| Guideline composite | A recommendation range or threshold that no guideline states |
| Estimand slippage | Efficacy, treatment-regimen, subgroup, or extension data mixed together |
| Intervention misattribution | Correct result assigned to the wrong mechanism or workflow |
| Secondary-source overreach | Review cited as if it generated primary data |
| Qualifier omission | "Rare," "selected patients," or "if tolerated" dropped |
| Direction reversal | Benefit, harm, or null finding framed in the wrong direction |
| Decorative citation | Citation appears in the reference list but supports no claim |

These are the cases that make a clinical answer look well sourced while quietly degrading trust.

## Release-Gate Use

This framework can be operated as a lightweight release gate:

1. Sample answers from high-use specialties and high-risk workflows.
2. Extract cited claims into a JSONL evaluation set.
3. Run structural verification automatically.
4. Adjudicate claim-level support on a focused sample.
5. Track failure rates by product surface, specialty, model version, retriever version, source type, and failure mode.
6. Block or review releases when high-severity failures rise above threshold.

Useful metrics:

- Structural citation pass rate
- Claim-level support rate
- High-severity unsupported claim rate
- Unsupported statistics per 100 cited answers
- Guideline-context error rate
- Secondary-source overreach rate
- Clean-control false positive rate

The clean-control rate matters. A useful evaluator must recognize well-grounded answers, not only find defects.

## One-Person Operating Model

One physician-scientist can own this lane without disturbing core engineering:

- Maintain a compact, adversarial clinical grounding eval set.
- Add 10 to 20 new cases per week from real product patterns, literature updates, and guideline changes.
- Convert adjudicated cases into structured JSONL with source links and corrected wording.
- Run weekly regression checks against candidate model, retriever, and prompt changes.
- Produce short failure-mode memos for engineering: what failed, why it failed, and what product layer should own the fix.
- Build specialty-specific eval packs for high-risk areas such as emergency medicine, cardiology, infectious disease, oncology, obstetrics, psychiatry, and revenue-cycle coding.

The output is not another review committee. It is a standing instrument panel for whether cited clinical AI answers remain faithful to the literature.

## Demonstration Package

This repository includes a small demo set at `examples/claim_grounding_cases.jsonl` and a no-dependency evaluator:

```bash
python scripts/evaluate_claim_grounding.py examples/claim_grounding_cases.jsonl
```

The demo intentionally includes clean controls alongside failures. The point is to demonstrate a measurable product loop: extract claims, classify support, assign severity, and track failure modes over time.

## Strategic Value

Medical AI companies compete on trust. Content partnerships, retrieval quality, and model performance matter only if the final answer preserves the relationship between claim and source. This framework turns that trust claim into a measurable engineering target.

The durable advantage is not a larger taxonomy. It is the ability to repeatedly identify the exact clinical situations where a system can cite real evidence and still mislead.
