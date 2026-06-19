#!/usr/bin/env python3
"""
assemble.py — Build one Sunny Side Up issue (one language) from a content JSON file.

Usage:
  python3 scripts/assemble.py --content content/issue-en.json \
      --settings config/settings.json \
      --template templates/email-template.html \
      --out examples/issue-en.html [--embed]

--embed : inline the local /assets images as data URIs (for previewing before
          GitHub Pages is live). Production runs WITHOUT --embed and uses hosted URLs.
"""
import argparse, base64, html, json, os, re

def esc(s): return html.escape(str(s), quote=True)

# ---------- section renderers (email-safe markup) ----------
def r_events(items):
    rows=[]
    for i,e in enumerate(items):
        border="" if i==len(items)-1 else "border-bottom:1px dashed #ECE3D4;"
        rows.append(f'<tr><td style="padding:9px 0;{border}"><strong style="color:#0D3347;font-size:15px;">{esc(e.get("day",""))} &middot; {esc(e["name"])}</strong><br><span style="color:#5D7079;font-size:13px;">{esc(e.get("meta",""))}</span></td></tr>')
    return '<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="font-family:\'Figtree\',Arial,sans-serif;">'+''.join(rows)+'</table>'

def r_blog(items):
    rows=[]
    for i,b in enumerate(items):
        border="" if i==len(items)-1 else "border-bottom:1px solid #ECE3D4;"
        rows.append(f'<tr><td style="padding:9px 0;{border}"><a href="{esc(b.get("url","#"))}" style="color:#0D3347;font-size:15px;font-weight:700;">{esc(b["title"])}</a><br><span style="color:#5D7079;font-size:13px;">{esc(b.get("tease",""))}</span></td></tr>')
    return '<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="font-family:\'Figtree\',Arial,sans-serif;">'+''.join(rows)+'</table>'

def r_deals(items):
    rows=[]
    for i,d in enumerate(items):
        rows.append(f'<tr><td bgcolor="#FFFFFF" style="background:#FFFFFF;border-radius:10px;padding:11px 13px;"><table role="presentation" width="100%"><tr><td><strong style="color:#0D3347;font-size:14px;">{esc(d["name"])}</strong><br><span style="color:#5D7079;font-size:12px;">{esc(d.get("desc",""))}</span></td><td align="right" valign="middle"><span style="background:#F58220;color:#FFFFFF;font-weight:700;font-size:12px;padding:5px 10px;border-radius:8px;">{esc(d.get("tag",""))}</span></td></tr></table></td></tr>')
        if i!=len(items)-1:
            rows.append('<tr><td height="8" style="font-size:0;line-height:0;">&nbsp;</td></tr>')
    return '<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="font-family:\'Figtree\',Arial,sans-serif;">'+''.join(rows)+'</table>'

def r_alist(items):
    rows=[]
    for i,a in enumerate(items):
        bg=a.get("emoji_bg","#E7F8F5")
        rows.append(f'<tr><td bgcolor="#FFFBF3" style="background:#FFFBF3;border:1px solid #ECE3D4;border-radius:14px;padding:14px;"><table role="presentation" width="100%"><tr><td width="56" valign="middle"><table role="presentation" width="48" cellpadding="0" cellspacing="0"><tr><td height="48" align="center" valign="middle" bgcolor="{bg}" style="background:{bg};border-radius:12px;font-size:20px;">{a.get("emoji","&#10024;")}</td></tr></table></td><td valign="middle" style="padding-left:12px;"><span style="font-size:11px;font-weight:700;letter-spacing:1px;text-transform:uppercase;color:#15C4AF;">{esc(a.get("cat",""))}</span><br><strong style="color:#0D3347;font-size:15px;">{esc(a["name"])}</strong><br><span style="color:#5D7079;font-size:13px;">{esc(a.get("desc",""))}</span> <a href="{esc(a.get("url","#"))}" style="color:#15C4AF;font-size:13px;font-weight:700;">{esc(a.get("cta","Learn more"))} &rarr;</a></td></tr></table></td></tr>')
        if i!=len(items)-1:
            rows.append('<tr><td height="10" style="font-size:0;line-height:0;">&nbsp;</td></tr>')
    return '<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="font-family:\'Figtree\',Arial,sans-serif;">'+''.join(rows)+'</table>'

def r_topbilling(t):
    return (f'<div style="font-family:\'Bricolage Grotesque\',\'Trebuchet MS\',Arial,sans-serif;font-size:24px;font-weight:700;color:#FFFFFF;line-height:1.15;padding:6px 0 8px;">{esc(t["title"])}</div>'
            f'<div style="font-family:\'Figtree\',Arial,sans-serif;font-size:14px;font-weight:700;color:#FFCA08;padding-bottom:8px;">{esc(t.get("when",""))}</div>'
            f'<div style="font-family:\'Figtree\',Arial,sans-serif;font-size:15px;line-height:1.55;color:#CFE2EE;padding-bottom:16px;">{esc(t.get("body",""))}</div>'
            f'<table role="presentation" cellpadding="0" cellspacing="0" border="0"><tr><td bgcolor="#F58220" style="border-radius:999px;"><a href="{esc(t.get("url","#"))}" style="display:inline-block;padding:12px 26px;font-family:\'Figtree\',Arial,sans-serif;font-size:14px;font-weight:700;color:#FFFFFF;text-decoration:none;border-radius:999px;">{esc(t.get("cta","Get the details"))} &rarr;</a></td></tr></table>')

def _photo(url, ph_bg, ph_color):
    if url:
        return f'<tr><td><img src="{esc(url)}" width="540" alt="" style="width:100%;height:auto;display:block;border-bottom:1px solid #ECE3D4;"></td></tr>'
    return f'<tr><td height="150" align="center" valign="middle" bgcolor="{ph_bg}" style="background:{ph_bg};height:150px;font-family:\'Figtree\',Arial,sans-serif;font-size:12px;color:{ph_color};">[ photo from the article ]</td></tr>'

def r_feature(f, ph_bg, ph_color, cta):
    title=f'<div style="font-family:\'Bricolage Grotesque\',\'Trebuchet MS\',Arial,sans-serif;font-size:22px;font-weight:700;color:#0D3347;padding:2px 0 10px;line-height:1.18;">{esc(f["title"])}</div>'
    card=('<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="border:1px solid #ECE3D4;border-radius:14px;overflow:hidden;">'
          + _photo(f.get("photo_url"), ph_bg, ph_color)
          + f'<tr><td style="padding:18px 20px;font-family:\'Figtree\',Arial,sans-serif;"><div style="font-size:15px;line-height:1.55;color:#1d2b34;padding-bottom:8px;">{esc(f.get("body",""))}</div><a href="{esc(f.get("url","#"))}" style="color:#15C4AF;font-weight:700;font-size:14px;">{esc(cta)} &rarr;</a></td></tr></table>')
    return title+card

def r_guide(g):
    return (f'<div style="font-family:\'Bricolage Grotesque\',\'Trebuchet MS\',Arial,sans-serif;font-size:23px;font-weight:700;color:#0D3347;padding:2px 0 10px;">{esc(g["title"])}</div>'
            f'<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" bgcolor="#FFF6D8" style="background:#FFF6D8;border:1px solid #F3E3A8;border-radius:16px;"><tr><td style="padding:20px;font-family:\'Figtree\',Arial,sans-serif;"><div style="font-size:15px;line-height:1.55;color:#1d2b34;padding-bottom:12px;">{esc(g.get("body",""))}</div><table role="presentation" cellpadding="0" cellspacing="0" border="0"><tr><td bgcolor="#F58220" style="border-radius:999px;"><a href="{esc(g.get("url","#"))}" style="display:inline-block;padding:12px 26px;font-family:\'Figtree\',Arial,sans-serif;font-size:14px;font-weight:700;color:#FFFFFF;text-decoration:none;border-radius:999px;">{esc(g.get("cta","Get the free guide"))} &rarr;</a></td></tr></table></td></tr></table>')

def r_realestate(re_, labels):
    def tile(url,ic,title,sub):
        return f'<a href="{esc(url)}" style="display:block;text-decoration:none;"><table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" bgcolor="#FFFBF3" style="background:#FFFBF3;border:1px solid #ECE3D4;border-radius:12px;"><tr><td align="center" style="padding:14px;font-family:\'Figtree\',Arial,sans-serif;"><div style="font-size:20px;">{ic}</div><div style="font-size:13px;font-weight:700;color:#0D3347;padding-top:4px;line-height:1.2;">{esc(title)}</div><div style="font-size:11.5px;color:#5D7079;">{esc(sub)}</div></td></tr></table></a>'
    return ('<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0"><tr>'
            f'<td class="stack" width="50%" valign="top" style="padding:0 5px 10px 0;">{tile(re_.get("open_url","#"),"&#127968;","Open Houses This Weekend","Tour homes Sat &amp; Sun")}</td>'
            f'<td class="stack" width="50%" valign="top" style="padding:0 0 10px 5px;">{tile(re_.get("new_url","#"),"&#10024;","New Homes on the Market","Just listed in Celebration")}</td>'
            '</tr><tr>'
            f'<td class="stack" width="50%" valign="top" style="padding:0 5px 0 0;">{tile(re_.get("search_url","#"),"&#127946;","Search of the Week",re_.get("search_label","This week\'s pick"))}</td>'
            f'<td class="stack" width="50%" valign="top" style="padding:0 0 0 5px;">{tile(re_.get("valuation_url","#"),"&#128176;","What\'s Your Home Worth?","Free instant valuation")}</td>'
            '</tr></table>')

def r_giveaway(g):
    return (f'<div style="font-family:\'Bricolage Grotesque\',\'Trebuchet MS\',Arial,sans-serif;font-size:25px;font-weight:800;color:#FFFFFF;padding:10px 0 8px;line-height:1.15;">{esc(g["title"])}</div>'
            f'<div style="font-size:15px;color:#FFFFFF;padding-bottom:16px;">{esc(g.get("body",""))}</div>'
            f'<table role="presentation" cellpadding="0" cellspacing="0" border="0" align="center"><tr><td bgcolor="#FFFFFF" style="border-radius:999px;"><a href="{esc(g.get("url","#"))}" style="display:inline-block;padding:13px 30px;font-family:\'Figtree\',Arial,sans-serif;font-size:15px;font-weight:700;color:#F58220;text-decoration:none;border-radius:999px;">{esc(g.get("cta","Enter to win"))} &rarr;</a></td></tr></table>')

def r_dyk(d):
    return (f'<div style="font-size:16px;font-weight:700;color:#0D3347;padding:6px 0 4px;">{esc(d["headline"])}</div>'
            f'<div style="font-size:13px;color:#5D7079;">{esc(d.get("body",""))}</div>')

# ---------- main ----------
def fill_region(html_text, name, inner):
    return re.sub(r'(<!--FILL:'+name+r'-->).*?(<!--/FILL-->)',
                  lambda m: m.group(1)+inner+m.group(2), html_text, count=1, flags=re.S)

def data_uri(path):
    with open(path,"rb") as f:
        return "data:image/png;base64,"+base64.b64encode(f.read()).decode()

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--content", required=True)
    ap.add_argument("--settings", required=True)
    ap.add_argument("--template", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--embed", action="store_true")
    a=ap.parse_args()
    c=json.load(open(a.content,encoding="utf-8"))
    s=json.load(open(a.settings,encoding="utf-8"))
    t=open(a.template,encoding="utf-8").read()
    here=os.path.dirname(os.path.dirname(os.path.abspath(a.settings)))

    # scalar FILL regions
    t=fill_region(t,"PREHEADER", esc(c.get("preheader","")))
    t=fill_region(t,"ISSUELINE", esc(c.get("issue_line","")))
    t=fill_region(t,"FORECAST", c.get("forecast",""))   # HTML allowed
    t=fill_region(t,"TOPBILLING", r_topbilling(c["top_billing"]))
    t=fill_region(t,"EVENTS", r_events(c.get("events",[])))
    t=fill_region(t,"BLOG", r_blog(c.get("blog",[])))
    t=fill_region(t,"STOREFRONT", r_feature(c["storefront"],"#E7F8F5","#9bb0ab",c["storefront"].get("cta","Read their story")))
    t=fill_region(t,"BRIGHTSPOT", r_feature(c["bright_spot"],"#FFF6D8","#b8a86a",c["bright_spot"].get("cta","Read the story")))
    t=fill_region(t,"GUIDE", r_guide(c["guide"]))
    t=fill_region(t,"REALESTATE", r_realestate(c["real_estate"],s))
    t=fill_region(t,"DEALS", r_deals(c.get("deals",[])))
    t=fill_region(t,"GIVEAWAY", r_giveaway(c["giveaway"]))
    t=fill_region(t,"DIDYOUKNOW", r_dyk(c["did_you_know"]))
    t=fill_region(t,"ALIST", r_alist(c.get("alist",[])))

    # guide eyebrow label (The Almanac / The Bright Pages)
    label=c["guide"].get("label","The Almanac")
    t=t.replace(">The Almanac<", ">"+esc(label)+"<", 1)

    # image tokens
    assets=s["assets"]; base=assets["base_url"].rstrip("/")
    def img(fn):
        return data_uri(os.path.join(here,"assets",fn)) if a.embed else f"{base}/{fn}"
    t=t.replace("{{LOGO_COLOR_URL}}", img(assets["logo_color"]))
    t=t.replace("{{LOGO_WHITE_URL}}", img(assets["logo_white"]))
    t=t.replace("{{SUNNI_HEAD_URL}}", img(assets["sunni_head"]))
    t=t.replace("{{SUNNI_FULL_URL}}", img(assets.get("sunni_full", assets["sunni_head"])))

    # link tokens (content.links overrides settings.links)
    links=dict(s.get("links",{})); links.update(c.get("links",{}))
    for tok,key in [("EVENTS_ALL_URL","events_all"),("BLOG_ALL_URL","blog_all"),("DEALS_ALL_URL","deals_all"),
                    ("ASK_SUNNI_URL","ask_sunni"),("FACEBOOK_URL","facebook"),("INSTAGRAM_URL","instagram"),
                    ("APP_URL","app"),("SUBMIT_URL","submit"),("NOMINATE_URL","nominate"),("LISTBIZ_URL","list_business")]:
        t=t.replace("{{"+tok+"}}", esc(links.get(key,"#")))

    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    open(a.out,"w",encoding="utf-8").write(t)
    print("Wrote", a.out, "(", len(t), "bytes )")

if __name__=="__main__":
    main()
