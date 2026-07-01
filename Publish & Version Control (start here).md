# Getting online + version control — plain English

Three parts. Do them in order. After each, come back and tell me it worked (or paste any error). Nothing here is risky, and your credentials are already protected from being published.

---

## Part 1 — Install Claude Code

Claude Code is the tool that lets us keep working on this project on your own machine, with proper version history built in.

1. Open **Terminal** (hold **⌘** and tap **Space**, type `Terminal`, press **Enter**).
2. Copy this line, paste it in (**⌘V**), press **Enter**:

```
curl -fsSL https://claude.ai/install.sh | bash
```

It downloads and installs. Wait until the blinking cursor returns.

3. **Quit Terminal completely** (⌘Q) and open it again. (This makes the new `claude` command available.)
4. Copy this line, paste it in, press **Enter**:

```
cd "/Users/apple/Desktop/Claude/Projects/ODCF Model" && claude
```

5. The first time, it asks you to log in. It opens your web browser — sign in with the **same account you use for Claude** (Claude Code needs a paid plan, which you already have).
6. When it finishes, you'll be looking at a Claude Code prompt, already inside your project. Type `hi` and press Enter to confirm it responds.

**Then come back here and tell me Part 1 worked.** (If anything turned red, paste it to me.)

---

## Part 2 — Version control + backup to GitHub

### Step 1 — Clear the half-finished history
Earlier attempts left a broken, incomplete version history. We start clean. Open a **new Terminal window** (⌘Space, `Terminal`, Enter) and paste:

```
cd "/Users/apple/Desktop/Claude/Projects/ODCF Model" && rm -rf .git && echo cleaned
```

This removes only the hidden history folder. **Your actual files are untouched.** If it prints `cleaned`, you're good.

### Step 2 — Create a free GitHub account
1. Go to **https://github.com** and click **Sign up**.
2. Pick a username (this becomes part of your site's web address, so choose something clean).
3. Confirm your email. That's it.

### Step 3 — Install GitHub Desktop
1. Go to **https://desktop.github.com** and download it.
2. Open the app. Click **Sign in to GitHub.com** and log in with the account you just made.

### Step 4 — Add and publish the project
1. In GitHub Desktop: menu **File → Add Local Repository**.
2. Choose the folder `/Users/apple/Desktop/Claude/Projects/ODCF Model`.
3. It will say the folder isn't a repository yet and offer to **create a repository here** — click that, then **Create Repository**.
4. Click the big **Publish repository** button.
5. **Uncheck** "Keep this code private" (it must be public for free hosting), then **Publish repository**.

Done: every change is now tracked, and there's a cloud backup. Your `secrets.ini` and the licensed catalogue data are automatically excluded.

**Come back and tell me your GitHub username and that it published.** Then we do Part 3 (going live).

---

## Part 3 — Go live with free hosting  *(after Part 2)*

1. On github.com, open your new repository.
2. **Settings → Pages → Source: Deploy from a branch → Branch: main, folder: / (root) → Save.**
3. Wait about a minute. Your site is then live at a public web address I'll help you find, in the form `https://YOUR-USERNAME.github.io/ODCF-Model/`.

From then on, publishing an update is one click in GitHub Desktop.

---

**Start with Part 1.** I'll be here for each step.
