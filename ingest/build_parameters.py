#!/usr/bin/env python3
"""
Build the CPF spatial-density profile empirically from the merged catalogue,
and enumerate DISCOS object classes for the fragmentation-potential mapping.

Outputs (../data/parameters/):
  - spatial_density_by_altitude.csv   (measured number density per altitude shell)
  - object_class_counts.csv           (DISCOS objectClass + Space-Track OBJECT_TYPE tallies)
"""
import os
import math
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
PROC = os.path.join(HERE, "..", "data", "processed")
PARAM = os.path.join(HERE, "..", "data", "parameters")
os.makedirs(PARAM, exist_ok=True)

R_EARTH = 6378.137  # km

df = pd.read_csv(os.path.join(PROC, "objects_merged.csv"), low_memory=False)
on = df[df["on_orbit"] & df["mean_altitude_km"].notna()].copy()
on = on[(on["mean_altitude_km"] >= 200) & (on["mean_altitude_km"] <= 2000)]  # LEO focus

# ---- spatial density by 25 km altitude shell ----
BIN = 25
rows = []
h = 200
while h < 2000:
    lo, hi = h, h + BIN
    shell = on[(on["mean_altitude_km"] >= lo) & (on["mean_altitude_km"] < hi)]
    n = len(shell)
    r1, r2 = R_EARTH + lo, R_EARTH + hi
    vol = (4.0 / 3.0) * math.pi * (r2**3 - r1**3)   # km^3
    dens = n / vol
    rows.append({
        "alt_low_km": lo, "alt_high_km": hi, "alt_mid_km": (lo + hi) / 2,
        "object_count": n,
        "shell_volume_km3": round(vol, 1),
        "spatial_density_per_km3": dens,
    })
    h += BIN

sd = pd.DataFrame(rows)
sd["cpf_normalized"] = sd["spatial_density_per_km3"] / sd["spatial_density_per_km3"].max()
sd.to_csv(os.path.join(PARAM, "spatial_density_by_altitude.csv"), index=False)

peak = sd.loc[sd["spatial_density_per_km3"].idxmax()]
print(f"[spatial density] LEO objects binned: {len(on):,}")
print(f"[spatial density] PEAK shell: {int(peak.alt_low_km)}-{int(peak.alt_high_km)} km "
      f"({int(peak.object_count)} objects, density {peak.spatial_density_per_km3:.3e}/km^3)")
print(f"[spatial density] saved spatial_density_by_altitude.csv ({len(sd)} shells)")

# ---- object class enumeration for FP mapping ----
disc = df["objectClass"].fillna("(none)").value_counts()
disc.to_csv(os.path.join(PARAM, "object_class_counts.csv"), header=["count"])
print("\n[object classes] DISCOS objectClass values:")
for k, v in disc.items():
    print(f"    {k:<32} {v:>7,}")
