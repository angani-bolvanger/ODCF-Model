#!/usr/bin/env python3
"""
ODCF Model - data ingestion.

Pulls the two catalogues the model needs and saves them into ../data/raw/:
  1. ESA DISCOS   -> physical attributes (mass, cross-section, object class, dimensions)
  2. Space-Track  -> orbital attributes (apogee, perigee, inclination, period, RCS, type)

They join on the NORAD id (DISCOS 'satno' == Space-Track 'NORAD_CAT_ID').

Usage:
    pip install requests
    python fetch_data.py                 # full pull of both catalogues
    python fetch_data.py --discos-limit 2000   # smaller DISCOS sample (faster first test)
    python fetch_data.py --skip-spacetrack     # only DISCOS
    python fetch_data.py --skip-discos         # only Space-Track

Credentials are read from secrets.ini in this folder.
"""

import argparse
import configparser
import csv
import os
import sys
import time

try:
    import requests
except ImportError:
    sys.exit("Missing dependency. Run:  pip install requests")

HERE = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.path.join(HERE, "..", "data", "raw")
DISCOS_BASE = "https://discosweb.esoc.esa.int"
ST_BASE = "https://www.space-track.org"

# DISCOS object fields we want for the model
DISCOS_FIELDS = (
    "name,cosparId,satno,objectClass,mass,shape,"
    "width,height,depth,diameter,span,"
    "xSectMax,xSectMin,xSectAvg,vimpelId"
)


def load_creds():
    cfg = configparser.ConfigParser()
    path = os.path.join(HERE, "secrets.ini")
    if not os.path.exists(path):
        sys.exit(f"secrets.ini not found at {path}")
    cfg.read(path)
    return cfg


def ensure_out():
    os.makedirs(OUT_DIR, exist_ok=True)


# ---------------------------------------------------------------- DISCOS
def fetch_discos(token, limit=None):
    """Page through /api/objects and write ../data/raw/discos_objects.csv."""
    session = requests.Session()
    session.headers.update({
        "Authorization": f"Bearer {token.strip()}",
        "DiscosWeb-Api-Version": "2",
        "Accept": "application/vnd.api+json",
    })

    out_path = os.path.join(OUT_DIR, "discos_objects.csv")
    url = f"{DISCOS_BASE}/api/objects"
    # Minimal, known-good query: just the page size. DISCOS returns all object
    # attributes by default, which is fine (we want the full physical profile anyway).
    params = {"page[size]": "100"}

    rows = []
    page = 0
    print("[DISCOS] starting catalogue pull ...")
    while url:
        r = session.get(url, params=params if page == 0 else None, timeout=60)
        if r.status_code == 429:
            wait = int(r.headers.get("Retry-After", "30"))
            print(f"[DISCOS] rate limited, sleeping {wait}s ...")
            time.sleep(wait + 1)
            continue
        if r.status_code == 401:
            sys.exit("[DISCOS] 401 Unauthorized - check your token in secrets.ini "
                     "(and that your DISCOSweb account is approved).")
        if r.status_code >= 400:
            # DISCOS returns a JSON:API 'errors' array explaining exactly what it disliked.
            print(f"[DISCOS] server rejected the request ({r.status_code}). It said:")
            try:
                for e in r.json().get("errors", [{"detail": r.text[:500]}]):
                    print("   -", e.get("title", ""), e.get("detail", ""))
            except Exception:
                print("   ", r.text[:500])
            sys.exit("[DISCOS] stopping so we can fix the query. Copy the lines above to Claude.")
        payload = r.json()
        for obj in payload.get("data", []):
            attr = obj.get("attributes", {})
            attr["id"] = obj.get("id")
            rows.append(attr)
        page += 1
        got = len(rows)
        print(f"[DISCOS] page {page}, {got} objects so far")
        if limit and got >= limit:
            rows = rows[:limit]
            break
        nxt = payload.get("links", {}).get("next")
        url = (DISCOS_BASE + nxt) if nxt and nxt.startswith("/") else nxt
        params = None
        time.sleep(0.4)  # be polite

    if not rows:
        print("[DISCOS] no rows returned.")
        return
    # union of keys, stable-ish order
    preferred = ["satno", "cosparId", "name", "objectClass", "mass", "shape",
                 "width", "height", "depth", "diameter", "span",
                 "xSectMax", "xSectMin", "xSectAvg", "active", "vimpelId", "id"]
    keys = preferred + [k for r in rows for k in r if k not in preferred]
    seen, cols = set(), []
    for k in keys:
        if k not in seen:
            seen.add(k); cols.append(k)
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        for row in rows:
            w.writerow(row)
    print(f"[DISCOS] DONE -> {out_path}  ({len(rows)} objects)")


# ------------------------------------------------------------ Space-Track
def fetch_spacetrack(username, password):
    """Log in and pull the current SATCAT to ../data/raw/spacetrack_satcat.csv."""
    session = requests.Session()
    print("[Space-Track] logging in ...")
    r = session.post(
        f"{ST_BASE}/ajaxauth/login",
        data={"identity": username.strip(), "password": password.strip()},
        timeout=60,
    )
    body = (r.text or "").strip()
    # A successful Space-Track login returns 200 with an empty body.
    # A failed one returns a short message containing "Login" / "Failed".
    if r.status_code != 200 or "fail" in body.lower() or ("login" in body.lower() and len(body) < 300):
        print(f"[Space-Track] login failed. Server replied (status {r.status_code}):")
        print("   ", body[:300] if body else "(empty)")
        sys.exit("[Space-Track] Most likely the account isn't approved yet, or the "
                 "username/password in secrets.ini is off. Copy the reply above to Claude.")

    query = (f"{ST_BASE}/basicspacedata/query/class/satcat/CURRENT/Y/"
             "orderby/NORAD_CAT_ID%20asc/format/csv")
    print("[Space-Track] login OK. Downloading current SATCAT (one big request) ...")
    r = session.get(query, timeout=300)
    r.raise_for_status()
    if r.text.lstrip().lower().startswith("<!doctype") or "<html" in r.text[:200].lower():
        sys.exit("[Space-Track] got a web page instead of data — the session wasn't "
                 "authenticated. Likely the account is still pending approval.")
    out_path = os.path.join(OUT_DIR, "spacetrack_satcat.csv")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(r.text)
    n = max(0, r.text.count("\n") - 1)
    print(f"[Space-Track] DONE -> {out_path}  ({n} rows)")
    # be a good citizen
    try:
        session.get(f"{ST_BASE}/ajaxauth/logout", timeout=30)
    except Exception:
        pass


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--discos-limit", type=int, default=None,
                    help="cap DISCOS objects (for a quick first test)")
    ap.add_argument("--skip-discos", action="store_true")
    ap.add_argument("--skip-spacetrack", action="store_true")
    args = ap.parse_args()

    cfg = load_creds()
    ensure_out()

    if not args.skip_discos:
        fetch_discos(cfg["discos"]["token"], limit=args.discos_limit)
    if not args.skip_spacetrack:
        fetch_spacetrack(cfg["spacetrack"]["username"], cfg["spacetrack"]["password"])

    print("\nAll done. Data is in:", os.path.abspath(OUT_DIR))
    print("Tell Claude it's ready and it will read + merge the catalogues.")


if __name__ == "__main__":
    main()
