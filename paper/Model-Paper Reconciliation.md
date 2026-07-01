# Model–Paper Reconciliation

Where the paper *Orbital Stewardship* and the implemented model/website currently diverge, and the exact change needed to bring the paper into correspondence. Three divergences; the first is substantive, the other two are minor.

---

## 1. Contribution basis — SUBSTANTIVE (changes the argument)

**Paper (current).** The annual contribution is an operator's share of the *total risk of all objects in orbit*, times the fund target:

> C_i = ( Σ_j ORS_ij / Σ_all-in-orbit ORS ) × T_annual

The denominator is described as "the total aggregated risk of all objects in orbit".

**Model (current).** The contribution is a levy on the *flow of new launches*, not the standing stock. A price per unit of risk is set from the annual launch flow, and each object pays that price times its score:

> price = T_annual / Σ_{j ∈ launched-in-window} ORS_j
> C_i = price × Σ_j ORS_ij

At a $1B target and recent launch rates this gives ≈ $1.06M per ORS point.

**Why the model changed this.** Dividing by the entire standing population (tens of thousands of objects, ~28% of which is orphan debris with no payer) produces negligible per-object figures — a high-risk object came out at ~$55k/yr. Pricing the flow attaches the cost to the launch decision and yields meaningful figures (~$744k/yr for the same object).

**Recommended paper edit.** Replace the contribution equation and the sentences around it (paras describing the "fraction of the total aggregated risk in orbit") with the flow formulation above. Suggested prose:

> "The annual contribution is levied on the flow of newly launched objects rather than on the entire standing population. A price per unit of risk is set by dividing the Total Annual Fund Target by the aggregate Orbital Risk Score of objects launched within the assessment window; each operator's contribution is that price multiplied by the total ORS of the objects it launches. Charging the standing stock would divide the target across the whole catalogue, including untraceable orphan debris for which no operator can be charged, and would reduce each contribution to a negligible sum. Pricing the flow of new activity instead attaches the cost to the decision that creates the risk, and preserves the incentive at the point of mission design."

---

## 2. ORS gating — MINOR (an addition, not a contradiction)

**Paper (current).** ORS = w_DGP·DGP + w_OPI·OPI + w_CPF·CPF (a weighted sum of the three normalised factors).

**Model (current).** The same weighted sum, then scaled by two gating factors:

> ORS = R(h_p) · A · ( w_DGP·DGP + w_OPI·OPI + w_CPF·CPF )

where **R** is a collision-relevance factor (1 for perigee within the populated LEO band, tapering to 0.25 above ~2000 km) and **A** discounts active, controllable objects (0.40 of the equivalent defunct object).

**Recommended paper edit.** Add a short passage after the ORS formula noting the two gating factors, so the paper's methodology matches the model. The weights themselves (0.30 / 0.50 / 0.20) already agree with the paper's example emphasis on persistence.

---

## 3. Cross-section placement — TRIVIAL

**Paper (current).** Lists collision cross-section as a sub-factor of DGP, while describing its effect as increasing "the probability of an object being struck."

**Model (current).** Places cross-section in the Collision Probability Factor (CPF), for exactly the reason the paper gives — a larger frontal area drives collision probability, not debris generation.

**Recommended paper edit.** One sentence: note that cross-section enters the score through the collision-probability term. This aligns the paper with its own description of the effect; no change to the substance.

---

## Status — applied 2 July 2026

**Items 1 and 2 have been applied to the paper** (`Orbital-Stewardship.docx` and the PDF), as clean text edits that touch no equation objects:

- The contribution equation was left unchanged. It did not need to change: the model's "price × ORS" is algebraically identical to the paper's "share × fund target" once the denominator is defined over the launch cohort. The reconciliation was therefore a change to the prose defining the denominator, now "the total aggregated risk of all objects launched within the assessment window", plus a sentence explaining the flow/levy rationale.
- A sentence was added after the ORS-weights sentence giving the gated form, ORS = R(hp)·A·(wDGP·DGP + wOPI·OPI + wCPF·CPF), and defining R and A.

**Item 3 needs no change.** The paper already describes cross-section's effect as increasing "the probability of an object being struck", which is exactly the collision-probability role the model assigns it. The grouping label differs but the substance agrees.

The document validated after packing (90 paragraphs in, 90 out; all checks passed). Your master draft in `Space Debris/Drafts/` was left untouched; replace it with this version if you want the change to propagate there too.
