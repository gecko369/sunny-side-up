#!/usr/bin/env python3
"""
push_to_mailchimp.py — Create a DRAFT Mailchimp campaign from a built HTML issue,
targeted to one language tag. It never sends; it only creates a draft for review.

Usage:
  python3 scripts/push_to_mailchimp.py --html examples/issue-en.html --lang en \
      --settings config/settings.json [--subject "..."] [--preview "..."]

Requires an environment variable MAILCHIMP_API_KEY (looks like: abc123...-us21).
The datacenter (us21, etc.) is read automatically from the end of the key.
"""
import argparse, json, os, sys
import requests
from requests.auth import HTTPBasicAuth

def _load_dotenv():
    """Load KEY=VALUE lines from a .env file in the repo root, if present."""
    root=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    path=os.path.join(root, ".env")
    if os.path.exists(path):
        for line in open(path, encoding="utf-8"):
            line=line.strip()
            if line and not line.startswith("#") and "=" in line:
                k,v=line.split("=",1)
                os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))

def main():
    _load_dotenv()
    ap=argparse.ArgumentParser()
    ap.add_argument("--html", required=True)
    ap.add_argument("--lang", required=True, choices=["en","es","pt"])
    ap.add_argument("--settings", required=True)
    ap.add_argument("--subject", default=None)
    ap.add_argument("--preview", default=None)
    a=ap.parse_args()

    key=os.environ.get("MAILCHIMP_API_KEY")
    if not key or "-" not in key:
        sys.exit("ERROR: set MAILCHIMP_API_KEY (format: xxxxxxxx-usXX)")
    dc=key.split("-")[-1]
    base=f"https://{dc}.api.mailchimp.com/3.0"
    auth=HTTPBasicAuth("anystring", key)

    s=json.load(open(a.settings,encoding="utf-8"))
    mc=s["mailchimp"]
    list_id=mc["audience_id"]
    tag_name=mc["tags"][a.lang]
    subject=a.subject or mc.get("subject",{}).get(a.lang,"Your week in Celebration")
    preview=a.preview or ""
    html=open(a.html,encoding="utf-8").read()

    # 1) find the static segment id for the language tag
    seg_id=None
    r=requests.get(f"{base}/lists/{list_id}/segments",
                   params={"type":"static","count":1000}, auth=auth, timeout=30)
    r.raise_for_status()
    for seg in r.json().get("segments",[]):
        if seg.get("name")==tag_name:
            seg_id=seg["id"]; break
    if seg_id is None:
        sys.exit(f"ERROR: tag/segment '{tag_name}' not found in audience {list_id}. "
                 f"Make sure at least one contact has that tag so Mailchimp creates the segment.")

    # 2) create the draft campaign targeted to that segment
    payload={
        "type":"regular",
        "recipients":{"list_id":list_id,"segment_opts":{"saved_segment_id":int(seg_id)}},
        "settings":{
            "subject_line":subject,
            "preview_text":preview,
            "title":f"Sunny Side Up ({a.lang.upper()}) - {subject}",
            "from_name":mc["from_name"],
            "reply_to":mc["reply_to"],
            "auto_footer":False
        }
    }
    r=requests.post(f"{base}/campaigns", json=payload, auth=auth, timeout=30)
    if r.status_code>=300:
        sys.exit(f"ERROR creating campaign: {r.status_code} {r.text}")
    cid=r.json()["id"]; web_id=r.json().get("web_id")

    # 3) set the HTML content
    r=requests.put(f"{base}/campaigns/{cid}/content", json={"html":html}, auth=auth, timeout=60)
    if r.status_code>=300:
        sys.exit(f"ERROR setting content: {r.status_code} {r.text}")

    print(f"DRAFT created [{a.lang}] -> campaign {cid} (web_id {web_id}) targeting tag '{tag_name}'. Review it in Mailchimp; it has NOT been sent.")

if __name__=="__main__":
    main()
