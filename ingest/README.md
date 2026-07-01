# Data fetcher — run me

This downloads the two catalogues the ODCF model needs, straight into `../data/raw/`.
Your credentials are already filled into `secrets.ini`, so you just run one command.

## One-time setup
Open Terminal and install the one dependency:

```
pip3 install requests
```

## Run it
From inside this `ingest` folder:

```
cd "/Users/apple/Claude/Projects/ODCF Model/ingest"
python3 fetch_data.py
```

- **DISCOS** pull pages through the whole catalogue and is rate-limited by ESA, so a full
  run can take 10–25 minutes. You'll see progress printed page by page.
- **Space-Track** is one big download at the end (a minute or two).

### Faster first test (optional)
To confirm both logins work before the long run, grab a small sample:

```
python3 fetch_data.py --discos-limit 500
```

When it finishes it prints "All done." Just tell me it's ready and I'll read and merge the data.

## Notes
- If DISCOS returns **401** or Space-Track says **login failed**, the account is probably
  still pending manual approval — wait for the approval email and rerun.
- `secrets.ini` holds your Space-Track password. It stays on your machine. You can delete it
  after fetching (you'll just need to re-add credentials to refresh later).
