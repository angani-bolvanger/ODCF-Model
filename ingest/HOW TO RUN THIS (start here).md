x # How to download the space data — plain English version

You don't need to understand any of this. Just copy, paste, press Enter. That's it.
There are two "copy-paste" steps. Total time: a couple of minutes of your effort, then it runs on its own.

---

## Step 1 — Open the black typing window (called "Terminal")

1. Hold down the **Command (⌘)** key and tap the **Spacebar**. A little search bar appears in the middle of your screen.
2. Type the word: **Terminal**
3. Press **Enter**.

A plain window opens with some text and a blinking cursor. This is where you paste things. (It looks intimidating. It isn't. You're just typing two instructions.)

---

## Step 2 — Copy and paste the FIRST line

Copy this exact line (click the copy button, or highlight and Cmd+C):

```
pip3 install requests
```

Click into the Terminal window, paste it (**Cmd+V**), and press **Enter**.

- It'll print a few lines. Wait until the blinking cursor comes back (a few seconds).
- **If a grey box pops up** saying it wants to install "command line developer tools," click **Install** and wait for it to finish (a few minutes), then try this line again.

---

## Step 3 — Copy and paste the SECOND line

Copy this whole line exactly (it's long — get all of it):

```
cd "/Users/apple/Claude/Projects/ODCF Model/ingest" && python3 fetch_data.py
```

Paste it into Terminal (**Cmd+V**) and press **Enter**.

Now it starts working. You'll see it printing progress like:

```
[DISCOS] page 1, 100 objects so far
[DISCOS] page 2, 200 objects so far
...
```

**This part takes about 15 minutes.** Just leave the window open and let it run. You can go do
something else. It's downloading the whole catalogue of objects in orbit, page by page.

When it's completely done, it prints:

```
All done.
```

---

## Step 4 — Tell me

Come back to our chat and just say **"it's done"** (or paste anything that looked like an error).
I'll take it from there.

---

## Want to do a 30-second test first? (optional)

If you'd rather check it works before the 15-minute run, use this line instead in Step 3.
It grabs just a small sample:

```
cd "/Users/apple/Claude/Projects/ODCF Model/ingest" && python3 fetch_data.py --discos-limit 500
```

If that finishes without errors, you know everything's set up — then you can run the full one.

---

## If something goes wrong

Don't worry about fixing it yourself. Just **copy whatever red or error text appears and paste it
to me in the chat.** Common ones:

- **"401" or "Unauthorized" or "login failed"** → your ESA / Space-Track accounts are probably
  still being approved by hand (can take a day or two). Wait for their approval emails, then rerun Step 3.
- **"command not found: python3"** → tell me and I'll give you a one-line fix.

That's genuinely all there is to it.
