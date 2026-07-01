#!/usr/bin/env python3
"""
Merge the DISCOS (physical) and Space-Track (orbital) catalogues into one table.

Join key: DISCOS 'satno' == Space-Track 'NORAD_CAT_ID'.

Output: ../data/processed/objects_merged.csv
  - DISCOS gives: mass, cross-section, object class, dimensions, predicted decay, fragments
  - Space-Track gives: inclination, apogee, perigee, period, RCS size, object type, decay, country
  - derived: mean_altitude_km, on_orbit
"""
import os
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(HERE, "..", "data", "raw")
PROC = os.path.join(HERE, "..", "data", "processed")
os.makedirs(PROC, exist_ok=True)

discos = pd.read_csv(os.path.join(RAW, "discos_objects.csv"), low_memory=False)
st = pd.read_csv(os.path.join(RAW, "spacetrack_satcat.csv"), low_memory=False)

# normalize join keys to nullable integers
discos["satno"] = pd.to_numeric(discos["satno"], errors="coerce").astype("Int64")
st["NORAD_CAT_ID"] = pd.to_numeric(st["NORAD_CAT_ID"], errors="coerce").astype("Int64")

discos_cols = ["satno", "cosparId", "name", "objectClass", "mass",
               "shape", "width", "height", "depth", "diameter", "span",
               "xSectMax", "xSectMin", "xSectAvg", "active",
               "predDecayDate", "cataloguedFragments", "onOrbitCataloguedFragments"]
discos_cols = [c for c in discos_cols if c in discos.columns]

st_cols = ["NORAD_CAT_ID", "OBJECT_TYPE", "OBJECT_NAME", "COUNTRY", "LAUNCH", "DECAY",
           "PERIOD", "INCLINATION", "APOGEE", "PERIGEE", "RCS_SIZE", "RCSVALUE"]
st_cols = [c for c in st_cols if c in st.columns]

merged = discos[discos_cols].merge(
    st[st_cols], how="outer", left_on="satno", right_on="NORAD_CAT_ID"
)
merged["norad_id"] = merged["satno"].fillna(merged["NORAD_CAT_ID"]).astype("Int64")

# derived fields
for c in ["APOGEE", "PERIGEE"]:
    merged[c] = pd.to_numeric(merged[c], errors="coerce")
merged["mean_altitude_km"] = (merged["APOGEE"] + merged["PERIGEE"]) / 2.0
merged["on_orbit"] = merged["DECAY"].isna() | (merged["DECAY"].astype(str).str.strip() == "")

merged = merged.drop(columns=["NORAD_CAT_ID"])
out = os.path.join(PROC, "objects_merged.csv")
merged.to_csv(out, index=False)

# report
print(f"DISCOS rows        : {len(discos):,}")
print(f"Space-Track rows   : {len(st):,}")
print(f"Merged rows        : {len(merged):,}")
matched = merged["satno"].notna() & merged["mean_altitude_km"].notna()
print(f"In BOTH catalogues : {int(matched.sum()):,}")
onorbit = merged[merged["on_orbit"]]
print(f"On orbit (no decay): {len(onorbit):,}")
have_mass = onorbit["mass"].notna().sum()
have_alt = onorbit["mean_altitude_km"].notna().sum()
have_x = onorbit["xSectAvg"].notna().sum()
print(f"  on-orbit w/ mass          : {have_mass:,}")
print(f"  on-orbit w/ altitude      : {have_alt:,}")
print(f"  on-orbit w/ cross-section : {have_x:,}")
full = onorbit[onorbit["mass"].notna() & onorbit["mean_altitude_km"].notna() & onorbit["xSectAvg"].notna()]
print(f"  on-orbit FULLY specified (mass+alt+xSect): {len(full):,}")
print(f"\nsaved -> {os.path.abspath(out)}")
