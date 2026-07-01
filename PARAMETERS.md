# ODCF Model — Stage 1 Parameter Documentation

**Project:** Orbital Debris Compensation Fund (ODCF) — operationalising the *Orbital Stewardship* paper as a transparent, data-driven risk model.
**Model type:** Transparent parametric (closed-form, auditable, browser-runnable).
**Date:** 2 July 2026.
**Scope of this document:** every parameter that feeds the Orbital Risk Score (ORS), where each value comes from, its role in the model, its units, and its current status. This is the reference that Stage 2 (the computation engine) and Stage 3 (the website explainer) build on.

---

## 1. What the model computes

The model assigns each orbiting object a composite **Orbital Risk Score (ORS)**, then converts an operator's aggregate ORS into their annual contribution to the fund.

**ORS (per object):**

> ORS = w_DGP · DGP + w_OPI · OPI + w_CPF · CPF

where DGP, OPI and CPF are each normalised to the interval [0, 1], and the three weights sum to 1.

**Contribution (per operator i):**

> C_i = ( Σ_j ORS_ij / Σ_all ORS ) × TotalAnnualFundTarget

An operator's payment is simply their share of the total risk in orbit, multiplied by the fund's annual budget target. This is the mechanism from the paper; the model's job is to compute the ORS values that drive it honestly and reproducibly.

The three factors capture three distinct dimensions of risk:

- **DGP — Debris Generation Potential:** how much debris this object would create if it broke up or was struck.
- **OPI — Orbital Persistence Index:** how long the object (and any debris from it) will linger in orbit.
- **CPF — Collision Probability Factor:** how crowded the object's orbital neighbourhood is.

---

## 2. The datasets behind the model

The model is built on a fusion of two authoritative catalogues, joined on the NORAD catalogue number (DISCOS `satno` = Space-Track `NORAD_CAT_ID`).

| Source | Role | What we pulled | Access |
|---|---|---|---|
| **ESA DISCOS** (DISCOSweb REST API) | Physical attributes | 91,591 objects: mass, average cross-section (`xSectAvg`), object class, dimensions, predicted decay date, catalogued-fragment counts | Free ESA account + API token |
| **Space-Track.org** (US catalogue) | Orbital attributes | 69,677 objects: inclination, apogee, perigee, period, RCS size, object type, decay status, country of origin | Free account (public stand-in for the non-public Space Fence feed) |

**Merged catalogue** (`data/processed/objects_merged.csv`): 91,668 objects. Of these:

- 67,504 appear in **both** catalogues (physical *and* orbital data);
- 56,385 are flagged on-orbit; 33,750 of those carry orbital elements;
- **20,975 on-orbit objects are fully specified** — mass *and* altitude *and* cross-section all present. These can be scored by the ORS directly, with no imputation.

The remaining on-orbit objects have partial data (typically orbital elements but no mass or cross-section, since DISCOS does not hold physical specs for every tracked fragment). Stage 2 will estimate the missing mass/area from RCS size and object type, and will tag every object as *measured* or *estimated* so the model never hides an assumption.

Data files are refreshable at any time by re-running `ingest/fetch_data.py`.

---

## 3. Factor 1 — Debris Generation Potential (DGP)

DGP quantifies how much lethal debris an object represents. It combines four sub-factors.

**3.1 Mass** — the primary driver of fragment count. Under the **NASA Standard Breakup Model**, the number of fragments larger than a characteristic length `Lc` scales with mass by a power law:

> N(>Lc) = 0.1 · (M_tot)^0.75 · Lc^(−1.71)

For a *catastrophic* collision, `M_tot` is the combined mass of both objects; for a non-catastrophic impact it is the projectile mass scaled by impact velocity. Mass is taken directly from the DISCOS `mass` field (kg). *(Exponents flagged for source verification — see §7.)*

**3.2 Cross-section** — a larger physical area is linearly more likely to be struck. Sourced from DISCOS `xSectAvg` (m²).

**3.3 Fragmentation potential (FP)** — the likelihood of a *spontaneous* breakup from stored energy (residual propellant, pressurised tanks, un-passivated batteries). Inferred from the object's class. We enumerated the actual DISCOS classes present in the catalogue and mapped each to an FP score (`data/parameters/object_class_fragmentation.csv`). Rocket bodies score highest (1.00 — frequently un-passivated with residual propellant); already-fragmented debris scores lowest (0.10–0.15); modern payloads default to a mid value pending passivation data.

**3.4 Material density** — denser fragments carry more kinetic energy per unit size and are more lethal. Using the ORDEM material categories (`data/parameters/material_density_categories.csv`): low ≈ 1.4 g/cm³ (plastics), medium ≈ 2.8 g/cm³ (aluminium, the baseline), high ≈ 8.0 g/cm³ (steel). Lethality multipliers are expressed relative to aluminium.

---

## 4. Factor 2 — Orbital Persistence Index (OPI)

OPI measures how long the object will pollute the commons. A longer orbital lifetime means a higher, more sustained risk contribution — and this is the factor the paper weights most heavily to enforce the 25-year post-mission-disposal guideline.

Orbital lifetime is governed by atmospheric drag, following **King-Hele decay theory**. The drivers are:

- **Altitude** (from Space-Track apogee/perigee) — the dominant variable; lifetimes range from months in the low hundreds of km to centuries or millennia above ~800 km.
- **Area-to-mass ratio** (DISCOS cross-section ÷ mass) — light, high-area objects decay faster.
- **Ballistic coefficient** B = m / (C_d · A), with the conventional LEO drag coefficient C_d = 2.2. *(Flagged for verification — see §7.)*
- **Atmospheric density**, modelled with a piecewise-exponential profile (`data/parameters/atmospheric_density_reference.csv`, Vallado Table 8-4 values), modulated by solar activity via the **F10.7 index** (freely available from NOAA SWPC).

A useful shortcut: DISCOS already publishes a **predicted decay date** (`predDecayDate`) for many objects, giving a direct lifetime signal we can use to anchor and cross-check the parametric estimate.

Lifetime is normalised to [0, 1] on a logarithmic scale, since raw lifetimes span several orders of magnitude.

---

## 5. Factor 3 — Collision Probability Factor (CPF)

CPF captures how crowded the object's orbital shell is. Rather than copy a static density curve from the literature, we **computed spatial density empirically from the merged catalogue itself** — a reproducible, measurement-based input (`data/parameters/spatial_density_by_altitude.csv`).

Method: on-orbit objects with known altitude were binned into 25 km shells from 200–2000 km; each shell's number density is its object count divided by the true spherical-shell volume (Earth radius 6378.137 km). The result is normalised to [0, 1] in the `cpf_normalized` column.

**Result — the profile shows two peaks:**

1. **A dominant peak at 475–500 km** (~4,700 objects; ~3.2 × 10⁻⁷ objects/km³) — the modern Starlink / active-payload congestion band.
2. **A broad secondary peak at ~775–850 km** — the classic debris peak that Kessler, Liou, Giudici and the wider literature all identify.

This is a meaningful validation: the catalogue independently reproduces the textbook ~800 km debris peak, while also surfacing the low-LEO congestion that the older modelling papers predate. The empirical density can later be scaled by ORDEM/MASTER small-debris flux to account for the untracked (<10 cm) population.

---

## 6. Weighting and policy levers

The three weights (w_DGP, w_OPI, w_CPF) are the fund's principal policy instruments, set and periodically reviewed by its governing body. The documented default is **w_DGP = 0.30, w_OPI = 0.50, w_CPF = 0.20**, reflecting the paper's explicit proposal to weight persistence heavily in the fund's early phase to drive compliance with disposal guidelines. These are defaults, not fixed constants — the model exposes them as adjustable inputs.

---

## 7. Known gaps and verification flags

In the spirit of a model that can be "taken seriously," the following are explicitly open:

- **Breakup-model exponents (0.75, −1.71)** and the **drag coefficient (C_d = 2.2)** are flagged `verify: true` in `ors_parameters.json`. They are standard textbook values; the verification pass will confirm them against the primary NASA breakup-model paper and King-Hele before they are treated as settled.
- **Missing physical data** for ~⅓ of on-orbit objects (mass/cross-section) will be imputed in Stage 2 from RCS size and object type, with every imputed value labelled as such.
- **Small-debris (<10 cm) flux** is not yet in the CPF; the empirical density covers the tracked population only. ESA MASTER / NASA ORDEM outputs (registration-gated downloads) can augment this later if desired.
- **Fragmentation-potential scores** are first-pass values based on object class; they can be refined with per-object passivation status where available.

---

## 8. File index

```
data/
  raw/
    discos_objects.csv            91,591 objects — DISCOS physical attributes
    spacetrack_satcat.csv         69,677 objects — Space-Track orbital attributes
  processed/
    objects_merged.csv            91,668 objects — joined on NORAD id (model's master table)
  parameters/
    ors_parameters.json           master parameter index (formula, weights, sources)
    spatial_density_by_altitude.csv   EMPIRICAL CPF profile (25 km shells)
    atmospheric_density_reference.csv Vallado piecewise-exponential atmosphere (OPI)
    material_density_categories.csv   ORDEM material density + lethality (DGP)
    object_class_fragmentation.csv    DISCOS class -> fragmentation-potential map (DGP)
    object_class_counts.csv           catalogue class tallies
ingest/
    fetch_data.py                 pulls both catalogues (re-runnable to refresh)
    merge_data.py                 joins DISCOS + Space-Track -> objects_merged.csv
    build_parameters.py           computes empirical spatial density + class counts
    secrets.ini                   API credentials (kept local, git-ignored)
```

---

## 9. Where this leads (Stage 2 preview)

With the parameter library in place, Stage 2 turns these inputs into a working computation engine: normalise each factor across the catalogue, compute the ORS for every object, aggregate by operator, and expose the contribution formula so a user can enter an object's characteristics and see its ORS and fund contribution. The transparent-parametric design means the whole calculation can run live in a browser for Stage 3 — no backend supercomputing, every number traceable to this document.
