#!/usr/bin/env python3
"""
assemble.py — Build one Sunny Side Up issue (one language) from a content JSON file.

Usage:
  python3 scripts/assemble.py --content content/issue-en.json --lang en \
      --settings config/settings.json --template templates/email-template.html \
      --out build/issue-en.html [--embed]

--lang  en | es | pt  (drives all the fixed UI text: labels, buttons, footer, etc.)
--embed inline local /assets images as data URIs (preview only; production omits it).
"""
import argparse, base64, datetime, html, json, os, re

def esc(s): return html.escape(str(s), quote=True)

DISPLAY = "'Bricolage Grotesque','Helvetica Neue',Helvetica,Arial,sans-serif"
BODY = "'Figtree',Arial,sans-serif"

# ---- Fixed UI text per language (HTML-ready; inserted raw) ----
STRINGS = {
"en": {
 "S_HEADER_EYEBROW":"Your week in Celebration","S_TAGLINE":"It's always sunny in Celebration.",
 "S_EY_FORECAST":"Sunni's Forecast","S_EY_TOPBILLING":"Top Billing",
 "S_EY_MARQUEE":"The Marquee","S_SUB_MARQUEE":"What's happening this weekend","S_BTN_EVENTS":"See all events",
 "S_EY_STORYBOARD":"The Storyboard","S_SUB_STORYBOARD":"Fresh off the press","S_BTN_BLOG":"See all the latest",
 "S_EY_STOREFRONT":"The Storefront","S_NOTE_STOREFRONT":"A featured local business. Want your story told? Just reply.",
 "S_EY_BRIGHTSPOT":"The Bright Spot","S_EY_KEYS":"Keys to Celebration","S_SUB_KEYS":"Celebration homes &amp; open houses this weekend",
 "S_RE_OPEN_T":"Open Houses This Weekend","S_RE_OPEN_S":"Tour homes Sat &amp; Sun",
 "S_RE_NEW_T":"New Homes on the Market","S_RE_NEW_S":"Just listed in Celebration",
 "S_RE_SEARCH_T":"Search of the Week","S_RE_WORTH_T":"What's Your Home Worth?","S_RE_WORTH_S":"Free instant valuation",
 "S_RE_DISCLAIMER":"Celebration Living Real Estate &middot; Powered by eXp Realty &middot; Equal Housing Opportunity",
 "S_EY_DEALS":"Sweet Deals","S_SUB_DEALS":"Save some dough &amp; support local",
 "S_DESC_DEALS":"Hand-picked perks from neighborhood favorites — just for Sunny Side Up readers. Go on, treat yourself, hunni.",
 "S_DEALS_REDEEM":"Just mention you found it at The Celebration Life","S_BTN_DEALS":"See all deals",
 "S_EY_LOCALLY":"Locally Loved","S_SUB_LOCALLY":"This week's town favorites",
 "S_DESC_LOCALLY":"A few of the local businesses our readers love — give 'em a visit.",
 "S_GIVEAWAY_BADGE":"This month's giveaway","S_EY_DYK":"Did You Know?",
 "S_EY_GETINVOLVED":"Get in on it","S_SUB_GETINVOLVED":"Three quick ways to join the fun",
 "S_INV1_T":"Got something going on?","S_INV1_D":"Hosting an event or running a deal? Drop the link — Sunni does the rest.",
 "S_INV2_T":"Nominate a neighbor","S_INV2_D":"Know a great local, business, or cause? Tell us who and why.",
 "S_INV3_T":"Is your business on the map?","S_INV3_D":"Get found by neighbors searching for what you do. List free in minutes.",
 "S_ASK_BADGE":"Coming soon","S_ASK_T":"Meet Sunni",
 "S_ASK_D":"Your Celebration concierge, hunni. Ask me what's happening this weekend, the nearest open chiropractor, or a few painters with good reviews — by text, by message, or tap to talk. I know the whole town.",
 "S_ASK_BTN":"Get first access","S_BACKYARD_T":"The Backyard","S_BACKYARD_D":"Where neighbors gather to swap recs, alerts &amp; finds.",
 "S_BACKYARD_BTN":"Pull up a chair","S_APP_T":"Celebration in Your Pocket","S_APP_D":"The whole town, on the go.","S_APP_BTN":"Get the app",
 "S_EY_LISTENING":"Sunni's Listening","S_LISTENING_T":"What'd I miss, hunni?",
 "S_LISTENING_D":"Hit reply and tell me what's happening in your neck of Celebration — I read every single one.",
 "S_SIGNOFF":"See you on the sunny side — Sunni","S_SIGNOFF_SUB":"Stay sweet, stay sunny.",
 "S_FOOTER_APP":"The App","S_FOOTER_LINE":"Celebration, FL &middot; You're getting this because you signed up for Sunny Side Up.",
 "S_FOOTER_UPDATE":"Update preferences","S_FOOTER_UNSUB":"Unsubscribe",
},
"es": {
 "S_HEADER_EYEBROW":"Tu semana en Celebration","S_TAGLINE":"Siempre hace sol en Celebration.",
 "S_EY_FORECAST":"El Pronóstico de Sunni","S_EY_TOPBILLING":"Lo Primero",
 "S_EY_MARQUEE":"La Cartelera","S_SUB_MARQUEE":"Qué hacer este fin de semana","S_BTN_EVENTS":"Ver todos los eventos",
 "S_EY_STORYBOARD":"Las Historias","S_SUB_STORYBOARD":"Recién salido del horno","S_BTN_BLOG":"Ver todo lo nuevo",
 "S_EY_STOREFRONT":"El Escaparate","S_NOTE_STOREFRONT":"Un negocio local destacado. ¿Quieres que contemos tu historia? Solo responde.",
 "S_EY_BRIGHTSPOT":"El Lado Bueno","S_EY_KEYS":"Las Llaves de Celebration","S_SUB_KEYS":"Casas y open houses en Celebration este fin de semana",
 "S_RE_OPEN_T":"Open Houses este fin de semana","S_RE_OPEN_S":"Visita casas sáb y dom",
 "S_RE_NEW_T":"Casas nuevas en el mercado","S_RE_NEW_S":"Recién listadas en Celebration",
 "S_RE_SEARCH_T":"Búsqueda de la semana","S_RE_WORTH_T":"¿Cuánto vale tu casa?","S_RE_WORTH_S":"Avalúo gratis al instante",
 "S_RE_DISCLAIMER":"Celebration Living Real Estate &middot; Con el respaldo de eXp Realty &middot; Igualdad de Oportunidades de Vivienda",
 "S_EY_DEALS":"Dulces Ofertas","S_SUB_DEALS":"Ahorra y apoya lo local",
 "S_DESC_DEALS":"Beneficios elegidos a mano de los favoritos del barrio — solo para los lectores de Sunny Side Up. Date un gusto, hunni.",
 "S_DEALS_REDEEM":"Solo menciona que lo viste en The Celebration Life","S_BTN_DEALS":"Ver todas las ofertas",
 "S_EY_LOCALLY":"Amados por Aquí","S_SUB_LOCALLY":"Los favoritos del pueblo esta semana",
 "S_DESC_LOCALLY":"Algunos negocios locales que nuestros lectores adoran — pásate a saludar.",
 "S_GIVEAWAY_BADGE":"El sorteo del mes","S_EY_DYK":"¿Sabías que...?",
 "S_EY_GETINVOLVED":"Súmate","S_SUB_GETINVOLVED":"Tres formas rápidas de sumarte",
 "S_INV1_T":"¿Tienes algo en marcha?","S_INV1_D":"¿Organizas un evento o tienes una promo? Comparte el enlace — Sunni hace el resto.",
 "S_INV2_T":"Nomina a un vecino","S_INV2_D":"¿Conoces a un buen vecino, negocio o causa? Cuéntanos quién y por qué.",
 "S_INV3_T":"¿Tu negocio está en el mapa?","S_INV3_D":"Que los vecinos te encuentren cuando buscan lo que ofreces. Regístrate gratis en minutos.",
 "S_ASK_BADGE":"Próximamente","S_ASK_T":"Conoce a Sunni",
 "S_ASK_D":"Tu concierge de Celebration, hunni. Pregúntame qué hacer este fin de semana, el quiropráctico abierto más cercano o unos pintores bien recomendados — por texto, por mensaje o toca para hablar. Conozco todo el pueblo.",
 "S_ASK_BTN":"Consigue acceso anticipado","S_BACKYARD_T":"El Patio","S_BACKYARD_D":"Donde los vecinos comparten recomendaciones, alertas y hallazgos.",
 "S_BACKYARD_BTN":"Toma asiento","S_APP_T":"Celebration en tu bolsillo","S_APP_D":"Todo el pueblo, donde vayas.","S_APP_BTN":"Descarga la app",
 "S_EY_LISTENING":"Sunni te escucha","S_LISTENING_T":"¿Qué me perdí, hunni?",
 "S_LISTENING_D":"Responde y cuéntame qué pasa en tu rincón de Celebration — leo todos y cada uno.",
 "S_SIGNOFF":"Nos vemos del lado soleado — Sunni","S_SIGNOFF_SUB":"Dulce y soleado, siempre.",
 "S_FOOTER_APP":"La App","S_FOOTER_LINE":"Celebration, FL &middot; Recibes esto porque te suscribiste a Sunny Side Up.",
 "S_FOOTER_UPDATE":"Actualizar preferencias","S_FOOTER_UNSUB":"Cancelar suscripción",
},
"pt": {
 "S_HEADER_EYEBROW":"Sua semana em Celebration","S_TAGLINE":"Em Celebration o sol nunca falta.",
 "S_EY_FORECAST":"A Previsão da Sunni","S_EY_TOPBILLING":"Destaque",
 "S_EY_MARQUEE":"A Programação","S_SUB_MARQUEE":"O que rola neste fim de semana","S_BTN_EVENTS":"Ver todos os eventos",
 "S_EY_STORYBOARD":"As Histórias","S_SUB_STORYBOARD":"Quentinho da redação","S_BTN_BLOG":"Ver as novidades",
 "S_EY_STOREFRONT":"A Vitrine","S_NOTE_STOREFRONT":"Um negócio local em destaque. Quer contar a sua história? É só responder.",
 "S_EY_BRIGHTSPOT":"O Lado Bom","S_EY_KEYS":"As Chaves de Celebration","S_SUB_KEYS":"Casas e open houses em Celebration neste fim de semana",
 "S_RE_OPEN_T":"Open Houses neste fim de semana","S_RE_OPEN_S":"Visite casas sáb e dom",
 "S_RE_NEW_T":"Casas novas no mercado","S_RE_NEW_S":"Recém-anunciadas em Celebration",
 "S_RE_SEARCH_T":"Busca da semana","S_RE_WORTH_T":"Quanto vale a sua casa?","S_RE_WORTH_S":"Avaliação grátis na hora",
 "S_RE_DISCLAIMER":"Celebration Living Real Estate &middot; Com o suporte da eXp Realty &middot; Igualdade de Oportunidade de Moradia",
 "S_EY_DEALS":"Ofertas Doces","S_SUB_DEALS":"Economize e valorize o comércio local",
 "S_DESC_DEALS":"Vantagens escolhidas a dedo dos queridinhos do bairro — só para quem lê a Sunny Side Up. Pode se mimar, hunni.",
 "S_DEALS_REDEEM":"É só dizer que viu na The Celebration Life","S_BTN_DEALS":"Ver todas as ofertas",
 "S_EY_LOCALLY":"Queridos da Cidade","S_SUB_LOCALLY":"Os favoritos da cidade nesta semana",
 "S_DESC_LOCALLY":"Alguns negócios locais que nossos leitores amam — faça uma visita.",
 "S_GIVEAWAY_BADGE":"O sorteio do mês","S_EY_DYK":"Você sabia?",
 "S_EY_GETINVOLVED":"Participe","S_SUB_GETINVOLVED":"Três jeitos rápidos de participar",
 "S_INV1_T":"Tem algo rolando?","S_INV1_D":"Vai organizar um evento ou tem uma promo? Mande o link — a Sunni cuida do resto.",
 "S_INV2_T":"Indique um vizinho","S_INV2_D":"Conhece um bom vizinho, negócio ou causa? Conte pra gente quem e por quê.",
 "S_INV3_T":"Seu negócio está no mapa?","S_INV3_D":"Seja encontrado pelos vizinhos que procuram o que você faz. Cadastre-se grátis em minutos.",
 "S_ASK_BADGE":"Em breve","S_ASK_T":"Conheça a Sunni",
 "S_ASK_D":"Sua concierge de Celebration, hunni. Me pergunte o que rola neste fim de semana, o quiroprático aberto mais perto ou uns pintores bem avaliados — por texto, por mensagem ou toque para falar. Eu conheço a cidade inteira.",
 "S_ASK_BTN":"Garanta acesso antecipado","S_BACKYARD_T":"O Quintal","S_BACKYARD_D":"Onde os vizinhos trocam dicas, alertas e achados.",
 "S_BACKYARD_BTN":"Puxe uma cadeira","S_APP_T":"Celebration no seu bolso","S_APP_D":"A cidade inteira, aonde você for.","S_APP_BTN":"Baixe o app",
 "S_EY_LISTENING":"A Sunni te ouve","S_LISTENING_T":"O que eu perdi, hunni?",
 "S_LISTENING_D":"Responda e me conte o que está rolando no seu cantinho de Celebration — eu leio cada mensagem.",
 "S_SIGNOFF":"Até o lado ensolarado — Sunni","S_SIGNOFF_SUB":"Doce e ensolarado, sempre.",
 "S_FOOTER_APP":"O App","S_FOOTER_LINE":"Celebration, FL &middot; Você recebe isto porque assinou a Sunny Side Up.",
 "S_FOOTER_UPDATE":"Atualizar preferências","S_FOOTER_UNSUB":"Cancelar inscrição",
},
}
GUIDE_LABELS = {
 "The Almanac":{"en":"The Almanac","es":"El Almanaque","pt":"O Almanaque"},
 "The Bright Pages":{"en":"The Bright Pages","es":"Las Páginas Brillantes","pt":"As Páginas Brilhantes"},
}

# ---------- section renderers ----------
def r_events(items):
    rows=[]
    for i,e in enumerate(items):
        b="" if i==len(items)-1 else "border-bottom:1px dashed #ECE3D4;"
        label=f'{esc(e.get("day",""))} &middot; {esc(e["name"])}'
        head=(f'<a href="{esc(e["url"])}" style="color:#0D3347;font-size:15px;font-weight:700;text-decoration:none;">{label}</a>'
              if e.get("url") else
              f'<strong style="color:#0D3347;font-size:15px;">{label}</strong>')
        rows.append(f'<tr><td style="padding:9px 0;{b}">{head}<br><span style="color:#5D7079;font-size:13px;">{esc(e.get("meta",""))}</span></td></tr>')
    return f'<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="font-family:{BODY};">'+''.join(rows)+'</table>'

def r_blog(items):
    rows=[]
    for i,b in enumerate(items):
        bd="" if i==len(items)-1 else "border-bottom:1px solid #ECE3D4;"
        rows.append(f'<tr><td style="padding:9px 0;{bd}"><a href="{esc(b.get("url","#"))}" style="color:#0D3347;font-size:15px;font-weight:700;">{esc(b["title"])}</a><br><span style="color:#5D7079;font-size:13px;">{esc(b.get("tease",""))}</span></td></tr>')
    return f'<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="font-family:{BODY};">'+''.join(rows)+'</table>'

def r_deals(items):
    rows=[]
    for i,d in enumerate(items):
        inner=f'<table role="presentation" width="100%"><tr><td><strong style="color:#0D3347;font-size:14px;">{esc(d["name"])}</strong><br><span style="color:#5D7079;font-size:12px;">{esc(d.get("desc",""))}</span></td><td align="right" valign="middle"><span style="background:#F58220;color:#FFFFFF;font-weight:700;font-size:12px;padding:5px 10px;border-radius:8px;">{esc(d.get("tag",""))}</span></td></tr></table>'
        if d.get("url"): inner=f'<a href="{esc(d["url"])}" style="display:block;text-decoration:none;color:inherit;">{inner}</a>'
        rows.append(f'<tr><td bgcolor="#FFFFFF" style="background:#FFFFFF;border-radius:10px;padding:11px 13px;">{inner}</td></tr>')
        if i!=len(items)-1: rows.append('<tr><td height="8" style="font-size:0;line-height:0;">&nbsp;</td></tr>')
    return f'<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="font-family:{BODY};">'+''.join(rows)+'</table>'

def r_alist(items):
    rows=[]
    for i,a in enumerate(items):
        bg=a.get("emoji_bg","#E7F8F5")
        cta=f'<span style="color:#15C4AF;font-size:13px;font-weight:700;white-space:nowrap;">{esc(a.get("cta","Learn more"))} &rarr;</span>'
        inner=f'<table role="presentation" width="100%"><tr><td width="56" valign="middle"><table role="presentation" width="48" cellpadding="0" cellspacing="0"><tr><td height="48" align="center" valign="middle" bgcolor="{bg}" style="background:{bg};border-radius:12px;font-size:20px;">{a.get("emoji","&#10024;")}</td></tr></table></td><td valign="middle" style="padding-left:12px;"><span style="font-size:11px;font-weight:700;letter-spacing:1px;text-transform:uppercase;color:#15C4AF;">{esc(a.get("cat",""))}</span><br><strong style="color:#0D3347;font-size:15px;">{esc(a["name"])}</strong><br><span style="color:#5D7079;font-size:13px;">{esc(a.get("desc",""))}</span> {cta}</td></tr></table>'
        if a.get("url"): inner=f'<a href="{esc(a["url"])}" style="display:block;text-decoration:none;color:inherit;">{inner}</a>'
        rows.append(f'<tr><td bgcolor="#FFFBF3" style="background:#FFFBF3;border:1px solid #ECE3D4;border-radius:14px;padding:14px;">{inner}</td></tr>')
        if i!=len(items)-1: rows.append('<tr><td height="10" style="font-size:0;line-height:0;">&nbsp;</td></tr>')
    return f'<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="font-family:{BODY};">'+''.join(rows)+'</table>'

def r_topbilling(t):
    return (f'<div style="font-family:{DISPLAY};font-size:24px;font-weight:700;color:#FFFFFF;line-height:1.15;padding:6px 0 8px;">{esc(t["title"])}</div>'
            f'<div style="font-family:{BODY};font-size:14px;font-weight:700;color:#FFCA08;padding-bottom:8px;">{esc(t.get("when",""))}</div>'
            f'<div style="font-family:{BODY};font-size:15px;line-height:1.55;color:#CFE2EE;padding-bottom:16px;">{esc(t.get("body",""))}</div>'
            f'<table role="presentation" cellpadding="0" cellspacing="0" border="0"><tr><td bgcolor="#F58220" style="border-radius:999px;"><a href="{esc(t.get("url","#"))}" style="display:inline-block;padding:12px 26px;font-family:{BODY};font-size:14px;font-weight:700;color:#FFFFFF;text-decoration:none;border-radius:999px;">{esc(t.get("cta","Get the details"))} &rarr;</a></td></tr></table>')

def r_feature(f, cta):
    photo = f'<tr><td><img src="{esc(f["photo_url"])}" width="540" alt="" style="width:100%;height:auto;display:block;border-bottom:1px solid #ECE3D4;"></td></tr>' if f.get("photo_url") else ""
    title=f'<div style="font-family:{DISPLAY};font-size:22px;font-weight:700;color:#0D3347;padding:2px 0 10px;line-height:1.18;">{esc(f["title"])}</div>'
    card=(f'<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="border:1px solid #ECE3D4;border-radius:14px;overflow:hidden;">'
          + photo
          + f'<tr><td style="padding:18px 20px;font-family:{BODY};"><div style="font-size:15px;line-height:1.55;color:#1d2b34;padding-bottom:8px;">{esc(f.get("body",""))}</div><a href="{esc(f.get("url","#"))}" style="color:#15C4AF;font-weight:700;font-size:14px;">{esc(cta)} &rarr;</a></td></tr></table>')
    return title+card

def r_guide(g):
    return (f'<div style="font-family:{DISPLAY};font-size:23px;font-weight:700;color:#0D3347;padding:2px 0 10px;">{esc(g["title"])}</div>'
            f'<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" bgcolor="#FFF6D8" style="background:#FFF6D8;border:1px solid #F3E3A8;border-radius:16px;"><tr><td style="padding:20px;font-family:{BODY};"><div style="font-size:15px;line-height:1.55;color:#1d2b34;padding-bottom:12px;">{esc(g.get("body",""))}</div><table role="presentation" cellpadding="0" cellspacing="0" border="0"><tr><td bgcolor="#F58220" style="border-radius:999px;"><a href="{esc(g.get("url","#"))}" style="display:inline-block;padding:12px 26px;font-family:{BODY};font-size:14px;font-weight:700;color:#FFFFFF;text-decoration:none;border-radius:999px;">{esc(g.get("cta","Get the free guide"))} &rarr;</a></td></tr></table></td></tr></table>')

def r_realestate(re_content, S, re_cfg):
    fixed=(re_cfg or {}).get("fixed",{})
    rot=(re_cfg or {}).get("search_of_week_rotation",[])
    open_url = fixed.get("open_houses_url") or re_content.get("open_url") or "#"
    new_url  = fixed.get("new_on_market_url") or re_content.get("new_url") or "#"
    val_url  = fixed.get("valuation_url") or re_content.get("valuation_url") or "#"
    # Search of the Week: skill override wins, else rotate by ISO week from config
    if re_content.get("search_url"):
        s_url=re_content["search_url"]; s_label=re_content.get("search_label") or ""
    elif rot:
        pick=rot[datetime.date.today().isocalendar()[1] % len(rot)]
        s_url=pick.get("url","#"); s_label=re_content.get("search_label") or pick.get("label","")
    else:
        s_url=re_content.get("search_url","#"); s_label=re_content.get("search_label","")
    def tile(url,ic,title,sub):
        return (f'<a href="{esc(url)}" style="display:block;text-decoration:none;"><table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" bgcolor="#FFFBF3" style="background:#FFFBF3;border:1px solid #ECE3D4;border-radius:12px;"><tr>'
                f'<td align="center" style="padding:14px;font-family:{BODY};"><div style="font-size:20px;">{ic}</div>'
                f'<div style="font-size:13px;font-weight:700;color:#0D3347;padding-top:4px;line-height:1.2;">{title}</div>'
                f'<div style="font-size:11.5px;color:#5D7079;">{sub}</div></td></tr></table></a>')
    return ('<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0"><tr>'
            f'<td class="stack" width="50%" valign="top" style="padding:0 5px 10px 0;">{tile(open_url,"&#127968;",S["S_RE_OPEN_T"],S["S_RE_OPEN_S"])}</td>'
            f'<td class="stack" width="50%" valign="top" style="padding:0 0 10px 5px;">{tile(new_url,"&#10024;",S["S_RE_NEW_T"],S["S_RE_NEW_S"])}</td>'
            '</tr><tr>'
            f'<td class="stack" width="50%" valign="top" style="padding:0 5px 10px 0;">{tile(s_url,"&#127946;",S["S_RE_SEARCH_T"],esc(s_label))}</td>'
            f'<td class="stack" width="50%" valign="top" style="padding:0 0 10px 5px;">{tile(val_url,"&#128176;",S["S_RE_WORTH_T"],S["S_RE_WORTH_S"])}</td>'
            '</tr></table>')

def r_giveaway(g):
    return (f'<div style="font-family:{DISPLAY};font-size:25px;font-weight:800;color:#FFFFFF;padding:10px 0 8px;line-height:1.15;">{esc(g["title"])}</div>'
            f'<div style="font-size:15px;color:#FFFFFF;padding-bottom:16px;">{esc(g.get("body",""))}</div>'
            f'<table role="presentation" cellpadding="0" cellspacing="0" border="0" align="center"><tr><td bgcolor="#FFFFFF" style="border-radius:999px;"><a href="{esc(g.get("url","#"))}" style="display:inline-block;padding:13px 30px;font-family:{BODY};font-size:15px;font-weight:700;color:#F58220;text-decoration:none;border-radius:999px;">{esc(g.get("cta","Enter to win"))} &rarr;</a></td></tr></table>')

def r_dyk(d):
    return (f'<div style="font-size:16px;font-weight:700;color:#0D3347;padding:6px 0 4px;">{esc(d["headline"])}</div>'
            f'<div style="font-size:13px;color:#5D7079;">{esc(d.get("body",""))}</div>')

# ---------- main ----------
def fill(h,name,inner):
    return re.sub(r'(<!--FILL:'+name+r'-->).*?(<!--/FILL-->)', lambda m:m.group(1)+inner+m.group(2), h, count=1, flags=re.S)

def data_uri(p):
    with open(p,"rb") as f: return "data:image/png;base64,"+base64.b64encode(f.read()).decode()

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--content",required=True); ap.add_argument("--settings",required=True)
    ap.add_argument("--template",required=True); ap.add_argument("--out",required=True)
    ap.add_argument("--lang",default="en",choices=["en","es","pt"]); ap.add_argument("--embed",action="store_true")
    a=ap.parse_args()
    c=json.load(open(a.content,encoding="utf-8")); s=json.load(open(a.settings,encoding="utf-8"))
    t=open(a.template,encoding="utf-8").read()
    S=STRINGS.get(a.lang,STRINGS["en"])
    here=os.path.dirname(os.path.dirname(os.path.abspath(a.settings)))
    re_cfg={}
    re_cfg_path=os.path.join(os.path.dirname(os.path.abspath(a.settings)),"real-estate.json")
    if os.path.exists(re_cfg_path):
        try: re_cfg=json.load(open(re_cfg_path,encoding="utf-8"))
        except Exception: re_cfg={}

    t=fill(t,"PREHEADER",esc(c.get("preheader","")))
    t=fill(t,"ISSUELINE",esc(c.get("issue_line","")))
    t=fill(t,"FORECAST",c.get("forecast",""))
    t=fill(t,"TOPBILLING",r_topbilling(c["top_billing"]))
    t=fill(t,"EVENTS",r_events(c.get("events",[])))
    t=fill(t,"BLOG",r_blog(c.get("blog",[])))
    t=fill(t,"STOREFRONT",r_feature(c["storefront"],c["storefront"].get("cta","Read their story")))
    t=fill(t,"BRIGHTSPOT",r_feature(c["bright_spot"],c["bright_spot"].get("cta","Read the story")))
    t=fill(t,"GUIDE",r_guide(c["guide"]))
    t=fill(t,"REALESTATE",r_realestate(c.get("real_estate",{}),S,re_cfg))
    t=fill(t,"DEALS",r_deals(c.get("deals",[])))
    t=fill(t,"GIVEAWAY",r_giveaway(c["giveaway"]))
    t=fill(t,"DIDYOUKNOW",r_dyk(c["did_you_know"]))
    t=fill(t,"ALIST",r_alist(c.get("alist",[])))

    glabel=c["guide"].get("label","The Almanac")
    t=t.replace("{{S_EY_GUIDE}}", esc(GUIDE_LABELS.get(glabel,{}).get(a.lang,glabel)))
    for k,v in S.items(): t=t.replace("{{"+k+"}}", v)

    A=s["assets"]; base=A["base_url"].rstrip("/")
    img=lambda fn:(data_uri(os.path.join(here,"assets",fn)) if a.embed else f"{base}/{fn}")
    t=t.replace("{{LOGO_COLOR_URL}}",img(A["logo_color"])).replace("{{LOGO_WHITE_URL}}",img(A["logo_white"]))
    t=t.replace("{{SUNNI_HEAD_URL}}",img(A["sunni_head"])).replace("{{SUNNI_FULL_URL}}",img(A.get("sunni_full",A["sunni_head"])))
    links=dict(s.get("links",{})); links.update(c.get("links",{}))
    links.setdefault("facebook_page", links.get("facebook","#"))  # brand page falls back to group if unset
    for tok,key in [("EVENTS_ALL_URL","events_all"),("BLOG_ALL_URL","blog_all"),("DEALS_ALL_URL","deals_all"),
                    ("ASK_SUNNI_URL","ask_sunni"),("FACEBOOK_URL","facebook"),("FACEBOOK_PAGE_URL","facebook_page"),
                    ("INSTAGRAM_URL","instagram"),("APP_URL","app"),("SUBMIT_URL","submit"),
                    ("NOMINATE_URL","nominate"),("LISTBIZ_URL","list_business")]:
        t=t.replace("{{"+tok+"}}",esc(links.get(key,"#")))

    os.makedirs(os.path.dirname(a.out),exist_ok=True)
    open(a.out,"w",encoding="utf-8").write(t)
    print(f"Wrote {a.out} [{a.lang}] ({len(t)} bytes, {t.count('{{')} leftover tokens)")

if __name__=="__main__": main()
