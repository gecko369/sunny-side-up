# SETUP — Sunny Side Up (the simple, no-tech-needed version)

This sets up your newsletter so it builds itself every week and leaves you 3 drafts to approve.
Go in order. Each step is small. You do **not** need to know any code.

> Your Mailchimp domain is already verified and your GHL → Mailchimp language tags already work. Nice — that's the hard part done.

---

## PHASE 1 — Put the files on GitHub (so Claude can reach them)

1. Download the **sunny-side-up.zip** I gave you and **unzip it** (double-click). You'll get a folder called `sunny-side-up`.
2. Go to **github.com**, sign in, click the **+** (top right) → **New repository**.
3. Owner: **gecko369**. Repository name: type exactly **`sunny-side-up`**. Set it to **Public**. Click **Create repository**.
4. On the next page click the link **"uploading an existing file."**
5. Open your unzipped `sunny-side-up` folder, select **everything inside it**, and **drag it onto the GitHub page**. Scroll down, click **Commit changes**.

*(Prefer GitHub Desktop? Drag the folder in, type a message, click Commit, then Push. Same result.)*

---

## PHASE 2 — Turn on free image hosting (GitHub Pages)

Your logo and Sunni images need a public web address. GitHub gives this for free.

1. In your repo, click **Settings** (top) → **Pages** (left menu).
2. Under **Source**, choose **Deploy from a branch**. Branch: **main**, folder: **/(root)**. Click **Save**.
3. Wait about 2 minutes.
4. Test it: open this in your browser →
   `https://gecko369.github.io/sunny-side-up/assets/logo-color.png`
   You should see your logo. ✅ (If not, wait a couple more minutes and refresh.)

---

## PHASE 3 — Fill in your details (edit two small files)

On GitHub, click a file → click the **pencil** ✏️ to edit → change the bits that say `REPLACE_ME` → click **Commit changes**.

1. **`config/settings.json`**
   - `reply_to`: change to **your email** (where replies should land).
   - Under `links`: paste your real **facebook** group URL, **instagram**, **app**, etc. (Leave any you don't have yet.)
2. **`config/real-estate.json`**
   - Paste your real **one-tap search URLs** from your celebrationlivingrealestate.com quick-search page (open houses, new on market, pool homes, etc.).

That's it for typing.

---

## PHASE 4 — Get your Mailchimp key (so Claude can make drafts)

1. In Mailchimp, click your **profile icon** → **Account & billing** → **Extras** → **API keys**.
2. Click **Create A Key**. Copy it. It looks like `abcd1234abcd1234-us21`.
3. Keep it private — you'll paste it in Phase 6. (Treat it like a password.)

---

## PHASE 5 — Do one test run (proves everything works)

1. Open **Claude Desktop** → **Claude Code** (or **Cowork**).
2. Point it at your repo: tell Claude **"Clone gecko369/sunny-side-up and open it,"** or open the local `sunny-side-up` folder.
3. Give Claude your key for this test: in the folder, create a file named **`.env`** containing one line:
   `MAILCHIMP_API_KEY=your-key-here`
4. Type: **"Run the sunny-side-up skill to build this week's newsletter drafts."**
5. Claude will pull content, build all three languages, and create **3 drafts in Mailchimp**.
6. Go to **Mailchimp → Campaigns**. You should see **3 drafts** (English, Spanish, Portuguese). Open them and check they look great.

*(If Claude mentions installing requirements, just say "yes" — it runs `pip install -r scripts/requirements.txt`.)*

---

## PHASE 6 — Make it automatic (hands-off)

**Option A — Recommended (runs even with your laptop closed): a cloud Routine**

1. **Claude Desktop → Routines → New routine → Remote.**
2. **Repository:** `gecko369/sunny-side-up`.
3. **Connectors:** turn on **Brilliant Directories**, **Google Drive**, and **Gmail**.
4. **Environment variable / secret:** add **`MAILCHIMP_API_KEY`** = your key.
5. **Prompt** (paste exactly):
   > Run the sunny-side-up skill in this repo to build this week's Sunny Side Up newsletter for the upcoming Thursday and create the 3 Mailchimp drafts (English, Spanish, Portuguese). Do not send anything. When done, email me a summary with the 3 draft links.
6. **Schedule:** Weekly · **Wednesday** · **7:00 AM** (your time zone).
7. **Save**, then click **Run now** once to test.

**Option B — Rock-solid fallback (needs your Mac on Wednesday morning): a Cowork task**

1. **Claude Desktop → Cowork →** type **`/schedule`**.
2. Use the same prompt as above; set Weekly · Wednesday · 7:00 AM.
3. Just keep Claude Desktop open on Wednesday mornings.

*(Use Option B if the cloud Routine ever can't reach Mailchimp. Both do the same thing.)*

---

## PHASE 7 — Your weekly 5 minutes

1. Open the Google Sheet **"Sunny Side Up — Weekly Editorial Inputs."**
2. Fill the row for the upcoming **Thursday**: Top Billing, Storefront, Bright Spot, giveaway, A-List members. (Later, your nomination/submission forms can fill this for you.)
3. **Wednesday:** the Routine builds 3 drafts and emails you the links.
4. **Thursday morning:** open Mailchimp, glance at each draft, click **Send** (or Schedule). Done. ☀️

---

## PHASE 8 — When you fully trust it (optional)

Tell me and I'll tweak the Routine prompt so it **schedules the send for Thursday 6:30 AM** automatically instead of leaving drafts — fully hands-off.

---

## If something looks off (quick fixes)

- **Images missing in the email?** GitHub Pages isn't on yet (Phase 2), or `base_url` in `settings.json` doesn't match your Pages address.
- **"tag/segment not found"?** Make sure at least one contact in Mailchimp carries each tag (`tcl_english_newsletter`, `tcl_espanol_newsletter`, `tcl_portugues_newsletter`) so Mailchimp has built those segments.
- **Spanish/Portuguese wording?** Have a native speaker skim the first 2–3 issues; after that, trust it.
- **Sender:** keep **From: Sunni · The Celebration Life `<sunni@livethecelebrationlife.com>`** and **Reply-To: your inbox** — best for landing in Primary.
