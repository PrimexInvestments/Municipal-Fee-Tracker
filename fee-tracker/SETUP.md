# Set It and Forget It — One-Time Setup Guide

After this setup (about 15 minutes of clicking, no typing code), you get:

- A real web address for your fee tracker, like `yourname.github.io/fee-tracker`
- Every morning at 7 AM Pacific, a robot checks the news, checks the
  municipal sites for rate changes, applies the safe ones, and republishes
  the site — while you sleep
- You never run Python. You never open a terminal. Ever.

It all runs on GitHub, which is free for this.

---

## Step 1 — Make a GitHub account (2 min)

1. Go to **github.com** and click **Sign up**
2. Follow the prompts (email, password, username — your username becomes
   part of your web address, so pick something you don't mind being public)

## Step 2 — Create a home for the files (2 min)

1. Once signed in, click the **+** in the top-right corner → **New repository**
2. Repository name: `fee-tracker` (or anything you like)
3. Leave it on **Public** (required for the free website hosting)
4. Click **Create repository**

## Step 3 — Upload the files (3 min)

1. On the page that appears, click the link that says
   **uploading an existing file**
2. Unzip `fee-tracker.zip` on your computer, then drag **everything inside
   the unzipped folder** into the upload box — including the `.github`
   folder if your computer shows it
3. Click **Commit changes** at the bottom

> **If the `.github` folder didn't upload** (some computers hide folders
> that start with a dot): in your repository, click **Add file → Create
> new file**. In the name box type exactly
> `.github/workflows/update.yml` — the slashes create the folders. Then
> open `update.yml` from the zip in any text editor (Notepad works),
> copy everything, paste it in, and click **Commit changes**.

## Step 4 — Turn on the website (2 min)

1. In your repository, click **Settings** (top menu) → **Pages** (left sidebar)
2. Under "Build and deployment", set **Source** to **Deploy from a branch**
3. Set **Branch** to `main` and folder to `/ (root)`, click **Save**
4. Wait a minute or two, refresh the page — a box appears with your live
   address. That link is your site. Bookmark it, share it.

## Step 5 — Turn on the daily robot (2 min)

1. Click the **Actions** tab (top menu)
2. If it asks, click the green button to enable workflows
3. You'll see **Daily fee tracker update** in the left list. Click it,
   then click **Run workflow → Run workflow** to test it right now
4. A yellow dot appears while it runs (~2 minutes), turning into a green
   check when done. That's a successful update.

From now on it runs itself every morning. The green checks and any
changes will accumulate without you doing anything.

---

## How you'll know something changed

Just open your site. The banner at the top recolours by itself:

- **Green** — all current, nothing due
- **Amber** — something is scheduled to change within 30 days
- **Red** — a known update date has passed; treat those rates as suspect

The **News** tab fills with new stories as the robot finds them (marked
UNREVIEWED until you read them). The **Change log** tab records every
rate the robot changed, with the old and new value — nothing is ever
changed silently.

## What the robot will and won't do

It **will** update the Metro Vancouver regional rates automatically when
their official page changes, because those parse reliably and every
change is logged.

It **won't** touch municipal rates (Vancouver DCLs, Burnaby, Surrey…).
Those mostly live in PDF bylaws that can't be read reliably, so the robot
flags them in the Change log for a human instead of guessing. When you
see one flagged, ask Claude to verify it against the bylaw and give you
updated files — then upload the changed files the same way as Step 3
(drag onto the repository page, Commit).

## If a morning run shows a red X

Click the Actions tab → click the failed run → the log shows which step
broke. Usually it's a municipal website being down, and the next morning
fixes itself. If it keeps failing, copy the error text and paste it to
Claude.
