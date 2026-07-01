#!/usr/bin/env python3
"""Generate assets/data.js (window.ODCF_DATA) from calibration + scored catalogue.
Uses the csv module (no pandas) to stay within workspace memory limits."""
import os, json, csv
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.join(HERE, "..")
calib = json.load(open(os.path.join(ROOT, "model", "calibration.json")))

WANT = ["ZARYA","HUBBLE","ENVISAT","STARLINK","ZENIT","DELTA 4","ARIANE 5","CZ-","IRIDIUM 33","ONEWEB","TERRA","COSMOS 2251"]
rows = []
with open(os.path.join(ROOT, "data", "processed", "scored_catalogue.csv")) as f:
    for r in csv.DictReader(f):
        try:
            if not r["mass"] or not r["xSectAvg"] or not r["env_alt_km"]:
                continue
            rows.append({"name": r["name"], "type": r.get("OBJECT_TYPE",""), "ors": round(float(r["ORS"]),3)})
        except Exception:
            continue
named, seen = [], set()
for w in WANT:
    for r in rows:
        if w in r["name"].upper() and r["name"] not in seen:
            named.append(r); seen.add(r["name"]); break
# spread across risk range
rows_sorted = sorted(rows, key=lambda x:-x["ors"])
step = max(1, len(rows_sorted)//8)
for r in rows_sorted[::step][:8]:
    if r["name"] not in seen:
        named.append(r); seen.add(r["name"])
comparison = [{"name":r["name"][:34],"type":r["type"],"ors":r["ors"]} for r in named[:20]]

CATEGORIES = [
  {"label":"Large active satellite (>1000 kg)","oc":"Payload","mass":2000,"xsect":15,"active":True,"alt":600},
  {"label":"Medium active satellite (250–1000 kg)","oc":"Payload","mass":500,"xsect":6,"active":True,"alt":550},
  {"label":"Small active satellite (50–250 kg)","oc":"Payload","mass":150,"xsect":2,"active":True,"alt":500},
  {"label":"CubeSat (<50 kg)","oc":"Payload","mass":10,"xsect":0.1,"active":True,"alt":450},
  {"label":"Defunct / non-operational satellite","oc":"Payload","mass":1000,"xsect":10,"active":False,"alt":800},
  {"label":"Rocket upper stage / body","oc":"Rocket Body","mass":2000,"xsect":12,"active":False,"alt":800},
  {"label":"Mission-related object","oc":"Payload Mission Related Object","mass":50,"xsect":1,"active":False,"alt":700},
  {"label":"Fragmentation debris","oc":"Payload Fragmentation Debris","mass":5,"xsect":0.05,"active":False,"alt":800},
]
OPERATORS = [["United States",34.5],["Unattributed / orphan debris",28.4],["Russia",18.2],["China",11.0],["France",2.2],["United Kingdom",1.4],["Japan",0.7],["India",0.4]]

payload = {"calib":calib,"comparison":comparison,"categories":CATEGORIES,"operators":OPERATORS}
out = os.path.join(ROOT, "assets", "data.js")
os.makedirs(os.path.dirname(out), exist_ok=True)
open(out,"w").write("window.ODCF_DATA="+json.dumps(payload,separators=(",",":"))+";\n")
print("comparison objects:", len(comparison))
print("wrote assets/data.js")
