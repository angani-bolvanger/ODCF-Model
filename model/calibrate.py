#!/usr/bin/env python3
"""
ODCF Model — Stage 2: calibration + full-catalogue scorer.

Reads the merged catalogue, computes the three ORS factors for every object,
derives normalization ranges from the real data, scores all objects, and writes:

  model/calibration.json          — constants the live (JS) engine needs
  data/processed/scored_catalogue.csv — every object with DGP/OPI/CPF/ORS

Design (transparent parametric; documented deviations from the paper):

  DGP  Debris Generation Potential — intrinsic breakup severity
       raw = mass^0.75  ×  material_lethality  ×  (0.5 + 0.5*FP)
       (mass^0.75 = NASA Standard Breakup Model fragment scaling;
        FP = fragmentation potential by object class; material default = aluminium)

  OPI  Orbital Persistence Index — how long it lingers
       lifetime = ESA DISCOS predDecayDate when available (authoritative),
       else a King-Hele-consistent altitude baseline scaled by ballistic coefficient.

  CPF  Collision Probability Factor — collision rate in its shell
       raw = spatial_density(altitude) × cross_section
       (cross-section lives here, not in DGP as the paper groups it, because a
        larger target area physically raises COLLISION probability — documented choice.)

  Each raw factor -> [0,1] by log min-max using 1st/99th percentiles (outlier-robust).
  ORS = w_DGP*DGP + w_OPI*OPI + w_CPF*CPF.
"""
import os, json, math, datetime
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
PROC = os.path.join(ROOT, "data", "processed")
PARAM = os.path.join(ROOT, "data", "parameters")

MU = 3.986004418e14        # m^3/s^2
R_EARTH_KM = 6378.137
CD = 2.2
SEC_PER_YEAR = 31557600.0
TODAY = datetime.date(2026, 7, 2)

WEIGHTS = {"DGP": 0.30, "OPI": 0.50, "CPF": 0.20}

# --- contribution (FLOW basis) ---
# The fund raises its annual target from the flow of NEW launches, priced by risk.
# price_per_ORS = FUND_TARGET / (average annual new-launch ORS over the window).
FUND_TARGET_USD = 1_000_000_000      # $1B/yr (fixed hypothetical policy target)
ASSESS_WINDOW_YR = 3                  # trailing window used to estimate annual flow

# --- balanced-blend gating (chosen design) ---
# Collision-relevance R(perigee): full weight in populated LEO, tapering above it,
# so nothing tops the list on longevity alone while parked far from traffic.
REL_FULL_KM = 1600.0     # <= this: fully collision-relevant
REL_TAPER_KM = 2000.0    # linear taper to REL_HIGH between FULL and this
REL_HIGH = 0.25          # MEO/GEO region floor (persistent but low cascade relevance)
REL_UNKNOWN = 0.5        # perigee unknown
# Active, controllable objects can avoid collisions and will be disposed:
ACTIVE_FACTOR = 0.40


def collision_relevance(perigee_km):
    if perigee_km is None or not np.isfinite(perigee_km):
        return REL_UNKNOWN
    if perigee_km <= REL_FULL_KM:
        return 1.0
    if perigee_km >= REL_TAPER_KM:
        return REL_HIGH
    frac = (perigee_km - REL_FULL_KM) / (REL_TAPER_KM - REL_FULL_KM)
    return 1.0 - frac * (1.0 - REL_HIGH)


def active_factor(active_val):
    if str(active_val).strip().lower() in ("true", "1", "1.0", "yes"):
        return ACTIVE_FACTOR
    return 1.0

# King-Hele-consistent baseline lifetime (years) for a REFERENCE ballistic
# coefficient (~100 kg/m^2), by altitude. Matches standard NASA/ESA rule-of-thumb
# decay times; scaled per-object by (B / B_ref). Anchors are widely published.
KH_ALT_KM   = [300,  400,  500,  600,  700,  800,  900, 1000, 1200, 1500, 2000]
KH_LIFE_YR  = [0.3,  1.0,  8.0,  30.0, 120, 350,  900, 2000, 8000, 30000, 200000]
B_REF = 100.0
LIFE_FLOOR_YR, LIFE_CAP_YR = 0.05, 100000.0

# ---- material lethality (default aluminium=1.0) ----
mat = pd.read_csv(os.path.join(PARAM, "material_density_categories.csv"))
MAT_DEFAULT = float(mat.loc[mat.category == "medium", "lethality_multiplier"].iloc[0])

# ---- fragmentation potential by object class ----
fp_df = pd.read_csv(os.path.join(PARAM, "object_class_fragmentation.csv"))
FP = dict(zip(fp_df.discos_object_class, fp_df.fp_score))
FP_DEFAULT = 0.5

# ---- empirical spatial density by altitude ----
sd = pd.read_csv(os.path.join(PARAM, "spatial_density_by_altitude.csv"))
def spatial_density(alt_km):
    if alt_km is None or not np.isfinite(alt_km): return np.nan
    row = sd[(sd.alt_low_km <= alt_km) & (sd.alt_high_km > alt_km)]
    if len(row): return float(row.spatial_density_per_km3.iloc[0])
    return float(sd.spatial_density_per_km3.min())  # outside 200-2000km -> sparse


def kh_lifetime_years(alt_km, ballistic_coeff):
    base = np.interp(alt_km, KH_ALT_KM, KH_LIFE_YR)
    scale = (ballistic_coeff / B_REF) if (ballistic_coeff and ballistic_coeff > 0) else 1.0
    return float(np.clip(base * scale, LIFE_FLOOR_YR, LIFE_CAP_YR))


def lifetime_years(row):
    # 1) authoritative: ESA predicted decay date
    pdd = row.get("predDecayDate")
    if isinstance(pdd, str) and pdd.strip():
        try:
            d = datetime.date.fromisoformat(pdd[:10])
            yrs = (d - TODAY).days / 365.25
            if yrs > 0: return float(np.clip(yrs, LIFE_FLOOR_YR, LIFE_CAP_YR))
        except Exception:
            pass
    # 2) King-Hele baseline scaled by ballistic coefficient.
    #    Use PERIGEE — for eccentric orbits, perigee drives atmospheric decay.
    alt = row.get("env_alt_km")
    if alt is None or not np.isfinite(alt): return np.nan
    m, A = row.get("mass"), row.get("xSectAvg")
    B = (m / (CD * A)) if (m and A and A > 0) else B_REF
    return kh_lifetime_years(alt, B)


def main():
    df = pd.read_csv(os.path.join(PROC, "objects_merged.csv"), low_memory=False)
    on = df[df["on_orbit"]].copy()

    # Environment altitude = perigee (where drag + traffic act); fall back to mean.
    on["env_alt_km"] = pd.to_numeric(on.get("PERIGEE"), errors="coerce")
    on["env_alt_km"] = on["env_alt_km"].fillna(on["mean_altitude_km"])

    # ---- raw factors ----
    def dgp_raw(r):
        m = r.get("mass")
        if not m or not np.isfinite(m) or m <= 0: return np.nan
        fp = FP.get(r.get("objectClass"), FP_DEFAULT)
        return (m ** 0.75) * MAT_DEFAULT * (0.5 + 0.5 * fp)

    def cpf_raw(r):
        alt, x = r.get("env_alt_km"), r.get("xSectAvg")
        if not x or not np.isfinite(x): return np.nan
        rho = spatial_density(alt)
        if not np.isfinite(rho): return np.nan
        return rho * x

    on["dgp_raw"] = on.apply(dgp_raw, axis=1)
    on["life_yr"] = on.apply(lifetime_years, axis=1)
    on["cpf_raw"] = on.apply(cpf_raw, axis=1)
    on["relevance"] = on["env_alt_km"].apply(collision_relevance)
    on["act_factor"] = on.get("active").apply(active_factor) if "active" in on.columns else 1.0

    # ---- calibration ranges (log, 1st/99th pct) ----
    def logrange(s):
        v = s.dropna(); v = v[v > 0]
        return float(np.log10(np.percentile(v, 1))), float(np.log10(np.percentile(v, 99)))

    dgp_lo, dgp_hi = logrange(on["dgp_raw"])
    life_lo, life_hi = math.log10(LIFE_FLOOR_YR), math.log10(LIFE_CAP_YR)
    cpf_lo, cpf_hi = logrange(on["cpf_raw"])

    def norm(s, lo, hi):
        return np.clip((np.log10(s.where(s > 0)) - lo) / (hi - lo), 0, 1)

    on["DGP"] = norm(on["dgp_raw"], dgp_lo, dgp_hi)
    on["OPI"] = norm(on["life_yr"], life_lo, life_hi)
    on["CPF"] = norm(on["cpf_raw"], cpf_lo, cpf_hi)
    on["ORS_core"] = (WEIGHTS["DGP"]*on["DGP"].fillna(0)
                    + WEIGHTS["OPI"]*on["OPI"].fillna(0)
                    + WEIGHTS["CPF"]*on["CPF"].fillna(0))
    # balanced blend: gate by collision-relevance and active-object discount
    on["ORS"] = on["ORS_core"] * on["relevance"] * on["act_factor"]

    # ---- FLOW-basis price per unit ORS (from recent-launch cohort) ----
    lyear = pd.to_numeric(on.get("LAUNCH").astype(str).str[:4], errors="coerce")
    cohort_ors = float(on.loc[lyear >= (TODAY.year - ASSESS_WINDOW_YR), "ORS"].sum())
    annual_flow_ors = cohort_ors / ASSESS_WINDOW_YR
    price_per_ors = FUND_TARGET_USD / annual_flow_ors if annual_flow_ors > 0 else 0.0

    # ---- outputs ----
    calibration = {
        "weights": WEIGHTS,
        "constants": {"MU": MU, "R_EARTH_KM": R_EARTH_KM, "CD": CD, "B_REF": B_REF,
                      "material_default": MAT_DEFAULT, "fp_default": FP_DEFAULT},
        "gating": {"rel_full_km": REL_FULL_KM, "rel_taper_km": REL_TAPER_KM,
                   "rel_high": REL_HIGH, "rel_unknown": REL_UNKNOWN,
                   "active_factor": ACTIVE_FACTOR},
        "normalization": {
            "DGP": {"type": "log10_minmax", "lo": dgp_lo, "hi": dgp_hi},
            "OPI": {"type": "log10_minmax", "lo": life_lo, "hi": life_hi,
                    "life_floor_yr": LIFE_FLOOR_YR, "life_cap_yr": LIFE_CAP_YR},
            "CPF": {"type": "log10_minmax", "lo": cpf_lo, "hi": cpf_hi},
        },
        "fp_by_class": FP,
        "kh_lifetime": {"alt_km": KH_ALT_KM, "life_yr": KH_LIFE_YR},
        "spatial_density": {"alt_low_km": sd.alt_low_km.tolist(),
                            "alt_high_km": sd.alt_high_km.tolist(),
                            "density": sd.spatial_density_per_km3.tolist()},
        "total_ors_sum": float(on["ORS"].sum()),
        "scored_count": int(on["ORS"].gt(0).sum()),
        "contribution": {
            "basis": "flow (annual new-launch levy)",
            "fund_target_usd": FUND_TARGET_USD,
            "assess_window_yr": ASSESS_WINDOW_YR,
            "annual_flow_ors": annual_flow_ors,
            "price_per_ors_usd": price_per_ors,
        },
        "generated": str(TODAY),
    }
    with open(os.path.join(HERE, "calibration.json"), "w") as f:
        json.dump(calibration, f, indent=2)

    cols = ["norad_id", "name", "objectClass", "OBJECT_TYPE", "COUNTRY", "active",
            "mass", "xSectAvg", "env_alt_km", "mean_altitude_km", "life_yr",
            "relevance", "act_factor", "DGP", "OPI", "CPF", "ORS_core", "ORS"]
    cols = [c for c in cols if c in on.columns]
    scored = on[cols].sort_values("ORS", ascending=False)
    scored.to_csv(os.path.join(PROC, "scored_catalogue.csv"), index=False)

    # ---- report ----
    scoreable = on["ORS"].gt(0).sum()
    print(f"on-orbit objects           : {len(on):,}")
    print(f"scored (ORS > 0)           : {int(scoreable):,}")
    print(f"DGP log-range (1-99 pct)   : {dgp_lo:.2f} .. {dgp_hi:.2f}")
    print(f"CPF log-range (1-99 pct)   : {cpf_lo:.2f} .. {cpf_hi:.2f}")
    print(f"\nTOP 12 RISKIEST OBJECTS (ORS):")
    top = scored.head(12)
    for _, r in top.iterrows():
        print(f"  ORS={r.ORS:.3f}  {str(r.get('name'))[:24]:<24} "
              f"{str(r.get('OBJECT_TYPE'))[:11]:<11} peri={r.get('env_alt_km'):>5.0f}km "
              f"m={r.get('mass'):>7.0f}kg life={r.get('life_yr'):>6.0f}yr")

    print(f"\nTOP OPERATORS by aggregate ORS share (fund contribution %):")
    agg = on.groupby(on["COUNTRY"].fillna("(unknown)"))["ORS"].sum().sort_values(ascending=False)
    total = agg.sum()
    for country, s in agg.head(10).items():
        print(f"  {country:<8} {100*s/total:5.1f}%   (ORS sum {s:,.0f})")
    print(f"\nsaved calibration.json + scored_catalogue.csv")


if __name__ == "__main__":
    main()
