# ODCF Model — Data Access Guide

This walks you through registering for the two credential-gated datasets the model needs.
Once you have them, paste the credentials back to me (see "How to give them to me" at the bottom).

---

## 1. ESA DISCOS (DISCOSweb) — object catalogue: mass, cross-section, type, dimensions

This is the backbone of the **Debris Generation Potential (DGP)** factor.

1. Go to **https://discosweb.esoc.esa.int**
2. Click **Register** (top right). Use your email (keystonessentials@gmail.com is fine).
3. Confirm via the email ESA sends, then log in.
4. Once logged in, go to your **account / profile page** and find **"API access"** or **"Tokens"**.
5. Click **Generate token** (sometimes "Create new token"). Copy the long string it gives you.
   - Treat this like a password.
6. That token is all I need to query the full catalogue programmatically.

**Note on approval:** ESA sometimes manually approves new DISCOSweb accounts (can take a day or two). If you can't generate a token immediately, that's why — just wait for the approval email.

---

## 2. Space-Track.org — US catalogue + TLEs (orbital state, altitude, inclination)

This feeds the **Orbital Persistence Index (OPI)** and **Collision Probability Factor (CPF)**.
It's the public stand-in for the (non-public) Space Fence raw data.

1. Go to **https://www.space-track.org**
2. Click **Create Account** (or "Request an account").
3. Fill in name, email, and a purpose statement. A simple true statement works, e.g.:
   *"Academic research: building a parametric risk model of the LEO debris environment for a paper on space-debris liability."*
4. Submit. **Approval is manual and usually takes 1–3 business days.** You'll get an email when active.
5. Once active, your **username + password** are what I use (Space-Track uses login-based API auth, not a token).

---

## 3. Optional but recommended later — NASA ORDEM / ESA MASTER

These are **downloadable engineering models**, not live APIs. We don't need them to start —
I'll use their *published reference density tables* from the papers you've already uploaded.
If you later want the real model outputs:

- **ESA MASTER**: request access at **https://sdup.esoc.esa.int** (free, registration-gated).
- **NASA ORDEM**: distributed by NASA's Orbital Debris Program Office; requires a formal software
  request (US-export-controlled). We'll likely **not** need the actual software — published ORDEM
  density/material tables are enough for a transparent parametric model.

I'll flag it clearly if we ever hit a wall that genuinely needs one of these.

---

## No-credential sources I can use immediately

- **Celestrak** (https://celestrak.org) — TLEs and derived catalogues, no login.
- **NOAA SWPC** — F10.7 solar flux (drives atmospheric density in the decay model), no login.
- Published **ORDEM / MASTER / IADC** density and material tables inside your uploaded PDFs.

So I can start building the parameter library now while your two accounts are approved.

---

## How to give me the credentials (when ready)

Just paste them into the chat like this:

```
DISCOS token: <the long string>
Space-Track username: <your username>
Space-Track password: <your password>
```

I'll use them only to pull the catalogue data for the model. If you'd rather not paste the
Space-Track password in chat, tell me and I'll instead give you a tiny script you run locally
that downloads the data and saves it into this folder — no password ever leaves your machine.
