# Sunny Side Up — Weekly Newsletter System

The self-running weekly newsletter for **The Celebration Life**, hosted by **Sunni**.
Each week it builds the issue in **English, Spanish, and Portuguese** and drops **3 Mailchimp drafts** for review.

## What's in here
```
sunny-side-up/
├── SKILL.md                  the "brain" — steps Claude follows each week
├── SETUP.md                  plain-English setup (start here)
├── templates/
│   └── email-template.html   the email (filled in automatically)
├── scripts/
│   ├── assemble.py           builds one issue from a content file
│   ├── push_to_mailchimp.py  creates a Mailchimp draft (never sends)
│   └── requirements.txt
├── config/
│   ├── settings.json         IDs, links, Mailchimp audience/tags, image URLs
│   ├── real-estate.json      fixed links + rotating "Search of the Week"
│   └── content-calendar.json seasonal guides + Did You Know rotation
├── content/
│   └── sample-content-en.json example issue content (the schema to follow)
├── assets/                   logo + Sunni images (hosted via GitHub Pages)
└── examples/                 a rendered preview issue
```

## How it runs (once a week)
1. You fill one row in the Google Sheet (~5 min).
2. Wednesday morning, the Claude Routine pulls events/blogs/deals, fills the template, translates EN→ES→PT, and creates 3 Mailchimp drafts.
3. It emails you the draft links.
4. Thursday you glance and hit Send.

**Start with [SETUP.md](SETUP.md).**
