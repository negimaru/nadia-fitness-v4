"""Build the whole v4 site from data/site.json.

Usage (from the repo root):  python3 tools/build.py

Generates every page (static HTML that works without JavaScript), sitemap.xml, robots.txt,
site.webmanifest, the timetable share image and the class placeholder images.
Read DESIGN.md before changing anything visual. Never hand-edit the generated HTML.
"""
import html
import json
import os
from collections import OrderedDict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = json.load(open(os.path.join(ROOT, "data", "site.json"), encoding="utf-8"))
S = D["studio"]
CLASSES = D["classes"]
BY_ID = {c["id"]: c for c in CLASSES}
SESSIONS = D["sessions"]
DAYS = D["days"]
SHORT = [d[:3] for d in DAYS]
SLOTS = ["Mañana", "Mediodía", "Tarde", "Noche"]
SITE = S["siteUrl"]                       # https://…/nadia-fitness-v4/
SITE_PATH = "/" + SITE.split("/", 3)[3]   # /nadia-fitness-v4/
V = {"css": 3, "js": 1}                   # bump to bust browser caches

e = html.escape
TEL = "tel:" + S["phoneIntl"]
WHATSAPP = "https://wa.me/" + S["whatsapp"] + "?text=" + __import__("urllib.parse").parse.quote(S["whatsappText"])
NEW_TAB = '<span class="sr-only"> (se abre en otra pestaña)</span>'


# ---------- helpers ----------
def minutes(t):
    h, m = t.split(":")
    return int(h) * 60 + int(m)


def slot_of(s):
    m = minutes(s["start"])
    return "Mañana" if m < 12 * 60 else "Mediodía" if m < 15 * 60 else "Tarde" if m < 19 * 60 else "Noche"


def name_of(s):
    return s["label"] or BY_ID[s["class"]]["name"]


def by_time(items):
    return sorted(items, key=lambda s: minutes(s["start"]))


def join_days(days):
    names = [SHORT[d] for d in days]
    return names[0] if len(names) == 1 else ", ".join(names[:-1]) + " y " + names[-1]


def when_lines(cid):
    """'Mar y Jue 16:30–17:30' lines, grouping days that share a time."""
    groups = OrderedDict()
    for s in sorted((s for s in SESSIONS if s["class"] == cid), key=lambda s: (s["day"], minutes(s["start"]))):
        key = f'{s["start"]}–{s["end"]}' + (f' · Int. {s["label"][-1]}' if s["label"] else "")
        groups.setdefault(key, [])
        if s["day"] not in groups[key]:
            groups[key].append(s["day"])
    keys = sorted(groups, key=lambda k: (groups[k][0], minutes(k.split("–")[0])))
    return [f"{join_days(groups[k])} {k}" for k in keys]


def first_start():
    return by_time(SESSIONS)[0]["start"]


def last_end():
    return max(SESSIONS, key=lambda s: minutes(s["end"]))["end"]


def ext(url, text, cls=""):
    """External link that opens a new tab and says so to screen readers."""
    c = f' class="{cls}"' if cls else ""
    return f'<a{c} href="{e(url)}" target="_blank" rel="noopener">{text}{NEW_TAB}</a>'


def img(p, photo, cls, sizes, eager=False, alt=None):
    """<img> with every smaller width variant (name-<w>.webp) that exists next to the file in srcset."""
    f = photo["file"]
    widths = [w for w in (240, 400, 480, 640, 800) if w < photo["w"]
              and os.path.exists(os.path.join(ROOT, "assets/img", f.replace(".webp", f"-{w}.webp")))]
    srcset = ""
    if widths:
        cands = [f'{p}assets/img/{f.replace(".webp", f"-{w}.webp")} {w}w' for w in widths] + [f'{p}assets/img/{f} {photo["w"]}w']
        srcset = f' srcset="{", ".join(cands)}" sizes="{sizes}"'
    loading = ' fetchpriority="high"' if eager else ' loading="lazy"'
    a = photo["alt"] if alt is None else alt
    return f'<img class="{cls}" src="{p}assets/img/{f}"{srcset} alt="{e(a)}" width="{photo["w"]}" height="{photo["h"]}"{loading}>'


def class_photo(c):
    if c["placeholder"]:
        return {"file": c["photo"], "alt": "", "w": 1200, "h": 750}
    return {"file": c["photo"], "alt": c["photoAlt"], "w": 840, "h": 840}


# ---------- icons (Lucide, 20px, decorative) ----------
def icon(body, cls="i"):
    return (f'<svg class="{cls}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" '
            f'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{body}</svg>')


I_PHONE = icon('<path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"/>')
I_MSG = icon('<path d="M7.9 20A9 9 0 1 0 4 16.1L2 22Z"/>')
I_SUN = icon('<circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.93 4.93l1.41 1.41M17.66 17.66l1.41 1.41M2 12h2M20 12h2M6.34 17.66l-1.41 1.41M19.07 4.93l-1.41 1.41"/>', "i i-sun")
I_MOON = icon('<path d="M12 3a6 6 0 0 0 9 9 9 9 0 1 1-9-9Z"/>', "i i-moon")
I_PRINT = icon('<polyline points="6 9 6 2 18 2 18 9"/><path d="M6 18H4a2 2 0 0 1-2-2v-5a2 2 0 0 1 2-2h16a2 2 0 0 1 2 2v5a2 2 0 0 1-2 2h-2"/><rect x="6" y="14" width="12" height="8"/>')

NAV = [("clases/", "Clases"), ("horario/", "Horario"), ("quien-soy/", "Quién soy"), ("contacto/", "Contacto")]


# ---------- layout ----------
def head(p, path, title, desc, og="og-nadia-fitness.jpg", og_alt="Logotipo de Nadia Fitness Dance Studio sobre bailarines"):
    canon = "" if path is None else f'<link rel="canonical" href="{SITE}{path}">\n<meta property="og:url" content="{SITE}{path}">\n'
    return f'''<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
<!-- Design proposal v4: remove this line when it replaces the live site -->
<meta name="robots" content="noindex">
{canon}<meta property="og:type" content="website">
<meta property="og:locale" content="es_ES">
<meta property="og:site_name" content="{e(S["name"])}">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:image" content="{SITE}assets/img/{og}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="{e(og_alt)}">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#16120F">
<link rel="icon" href="{p}assets/img/favicon.svg?v=2" type="image/svg+xml">
<link rel="apple-touch-icon" href="{p}assets/img/apple-touch-icon.png">
<link rel="manifest" href="{p}site.webmanifest">
<script>document.documentElement.classList.add("js");try{{var t=localStorage.getItem("nf4-theme");if(t)document.documentElement.setAttribute("data-theme",t)}}catch(e){{}}</script>
<link rel="preload" href="{p}assets/fonts/barlow-condensed-800-normal-latin.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="{p}assets/fonts/instrument-sans-normal-latin.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="{p}assets/css/site.css?v={V["css"]}">
<script type="application/ld+json">{json_ld()}</script>
<script src="{p}assets/js/site.js?v={V["js"]}" defer></script>
</head>
'''


def header(p, current):
    home = p or "./"
    items = [f'<li><a href="{home}"{" aria-current=\"page\"" if current == "" else ""}><span class="n n-blank" aria-hidden="true">00</span>Inicio</a></li>']
    for i, (href, label) in enumerate(NAV, 1):
        cur = ' aria-current="page"' if current == href else ""
        items.append(f'<li><a href="{p}{href}"{cur}><span class="n" aria-hidden="true">0{i}</span>{label}</a></li>')
    items.append(f'<li class="menu-phone"><a href="{TEL}">{S["phone"]}</a></li>')
    return f'''<body>
<a class="skip" href="#main">Saltar al contenido</a>
<header class="band">
<div class="wrap band-in">
<a class="brand" href="{home}"><img src="{p}assets/img/logo-280.webp" srcset="{p}assets/img/logo-140.webp 140w, {p}assets/img/logo-200.webp 200w, {p}assets/img/logo-280.webp 280w, {p}assets/img/logo-340.webp 340w, {p}assets/img/logo-400.webp 400w" sizes="95px" alt="{e(S["name"])}, inicio" width="110" height="60"></a>
<nav class="nav" aria-label="Principal">
<button class="burger" type="button" aria-expanded="false" aria-controls="menu" aria-label="Abrir menú"><span></span><span></span><span></span></button>
<ul id="menu">{"".join(items)}</ul>
</nav>
<a class="band-phone" href="{TEL}">{S["phone"]}</a>
<button class="theme" type="button" aria-label="Cambiar a modo oscuro">{I_MOON}{I_SUN}</button>
</div>
</header>
'''


def footer(p):
    home = p or "./"
    calls = "".join(f'<li><span>{DAYS[c["day"]]}</span><span>{c["from"]}–{c["to"]}</span></li>' for c in D["callHours"])
    pages = "".join(f'<li><a href="{p}{h}">{l}</a></li>' for h, l in [("", "Inicio")] + NAV).replace('href=""', f'href="{home}"')
    return f'''<footer class="foot">
<div class="wrap foot-grid">
<div><img class="foot-logo" src="{p}assets/img/logo-280.webp" srcset="{p}assets/img/logo-140.webp 140w, {p}assets/img/logo-200.webp 200w, {p}assets/img/logo-280.webp 280w, {p}assets/img/logo-340.webp 340w, {p}assets/img/logo-400.webp 400w" sizes="95px" alt="" width="110" height="60" loading="lazy">
<p>{e(S["tagline"])}.</p>
<p>{ext(S["instagram"], e(S["instagramHandle"]))} · {ext(S["facebook"], "Facebook")}</p></div>
<div><h2 class="label">Contacto</h2><p><a href="{TEL}">{S["phone"]}</a><br>{ext(WHATSAPP, "WhatsApp")}</p>
<p>{e(S["street"])}<br>{S["postalCode"]} {e(S["locality"])}, {e(S["region"])}</p></div>
<div><h2 class="label">Horario de llamadas</h2><ul class="foot-calls">{calls}</ul></div>
<div><h2 class="label">Páginas</h2><ul class="foot-pages">{pages}</ul></div>
</div>
<div class="wrap foot-legal"><p>© <span id="year">2026</span> {e(S["name"])} · {e(S["locality"])}</p>
<p><a href="{p}aviso-legal/">Aviso legal</a> · <a href="{p}privacidad/">Privacidad</a> · Propuesta de diseño v4</p></div>
<nav class="callbar" aria-label="Contacto rápido"><a class="callbar-call" href="{TEL}">{I_PHONE}Llamar</a>{ext(WHATSAPP, I_MSG + "WhatsApp", "callbar-wa")}</nav>
</footer>
<script type="application/json" id="nf-data">{client_data()}</script>
</body>
</html>
'''


def client_data():
    """Minimal data for the JS enhancements (Hoy board, call status). Same source as the HTML."""
    return json.dumps({
        "days": DAYS, "callHours": D["callHours"], "whatsapp": WHATSAPP,
        "sessions": [{"day": s["day"], "start": s["start"], "end": s["end"], "name": name_of(s), "note": s["note"],
                      "type": BY_ID[s["class"]]["type"]} for s in SESSIONS],
    }, ensure_ascii=False).replace("</", "<\\/")


def json_ld():
    data = {
        "@context": "https://schema.org", "@type": "SportsActivityLocation", "name": S["name"],
        "description": S["tagline"] + ": grupos de dance por niveles, Fitdance, PowerHIIT y Aquafitness.",
        "url": SITE, "telephone": S["phoneIntl"], "image": SITE + "assets/img/og-nadia-fitness.jpg",
        "address": {"@type": "PostalAddress", "streetAddress": S["street"], "postalCode": S["postalCode"],
                    "addressLocality": S["locality"], "addressRegion": S["region"], "addressCountry": S["country"]},
        "geo": {"@type": "GeoCoordinates", "latitude": S["geo"]["lat"], "longitude": S["geo"]["lng"]},
        "hasMap": S["mapsUrl"], "areaServed": S["areaServed"], "sameAs": [S["instagram"], S["facebook"]],
        "openingHoursSpecification": [{"@type": "OpeningHoursSpecification",
                                       "dayOfWeek": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
                                       "opens": first_start().zfill(5), "closes": last_end().zfill(5)}],
        "makesOffer": [{"@type": "Offer", "itemOffered": {"@type": "Service", "name": c["name"], "description": c["summary"]}} for c in CLASSES],
    }
    return json.dumps(data, ensure_ascii=False).replace("</", "<\\/")


# ---------- components ----------
def kind_label(c):
    return f'{c["kind"]} · {c["audience"]}'


def today_board(p):
    """Static fallback; site.js replaces it with today's real classes (now / next)."""
    return f'''<aside class="today" aria-labelledby="today-title">
<p class="label"><span class="live" aria-hidden="true"></span>Hoy en el estudio</p>
<h2 class="today-date" id="today-title">De lunes a viernes</h2>
<p class="today-fallback">Clases de {first_start()} a {last_end()}.</p>
<ol class="today-list"></ol>
<p class="today-foot"><a href="{p}horario/">Ver la semana completa →</a></p>
</aside>'''


def class_lists(p, detail=False):
    """Two lists (rule 8): 4 dance classes, then 3 fitness classes."""
    out = []
    n = 0
    for group, title in (("dance", "Baile"), ("fit", "Fitness")):
        items = [c for c in CLASSES if c["type"] == group]
        rows = []
        for c in items:
            n += 1
            when = "".join(f"<li>{w}</li>" for w in when_lines(c["id"]))
            photo = img(p, class_photo(c), "cl-photo" + (" is-placeholder" if c["placeholder"] else ""), "(max-width: 860px) 100vw, 320px")
            if detail:
                rows.append(f'''<article class="cd" id="{c["id"]}">
<span class="cl-num">{n:02d}</span>
<div class="cd-main">
<p class="cl-aud">{e(kind_label(c))}</p>
<h3 class="cd-name"><span class="dot dot-{c["type"]}" aria-hidden="true"></span>{e(c["name"])}</h3>
<p class="cd-desc">{e(c["description"])}</p>
<ul class="cl-when" aria-label="Horario de {e(c["name"])}">{when}</ul>
<p class="cd-actions"><a class="link-cta" href="{p}contacto/?clase={c["id"]}">Reservar plaza <span aria-hidden="true">→</span></a><a class="link-cta link-quiet" href="{p}horario/?clase={c["id"]}">Ver en el horario <span aria-hidden="true">→</span></a></p>
</div>
{photo}
</article>''')
            else:
                rows.append(f'''<li class="cl-row">
<span class="cl-num">{n:02d}</span>
<div class="cl-main">
<h4 class="cl-name"><span class="dot dot-{c["type"]}" aria-hidden="true"></span><a href="{p}clases/#{c["id"]}">{e(c["name"])}</a></h4>
<p class="cl-desc">{e(c["summary"])}</p>
</div>
<div class="cl-meta"><p class="cl-aud">{e(kind_label(c))}</p><ul class="cl-when">{when}</ul></div>
</li>''')
        hl = "h2" if detail else "h3"
        body = "\n".join(rows) if detail else f'<ol class="cl-list" start="{n - len(items) + 1}">' + "\n".join(rows) + "</ol>"
        out.append(f'<div class="cl-group"><{hl} class="cl-group-title"><span class="dot dot-{group}" aria-hidden="true"></span>{title} <span class="count">{len(items)} clases</span></{hl}>\n{body}\n</div>')
    return "\n".join(out)


def legend():
    return '<p class="legend"><span><span class="dot dot-dance" aria-hidden="true"></span>Baile</span><span><span class="dot dot-fit" aria-hidden="true"></span>Fitness</span></p>'


def timetable(p, heading_level=3):
    def item(s):
        c = BY_ID[s["class"]]
        note = f'<small>{e(s["note"])}</small>' if s["note"] else ""
        return f'<li class="tt-item tt-{c["type"]}" data-class="{c["id"]}"><time>{s["start"]}–{s["end"]}</time>{e(name_of(s))}{note}</li>'
    head_row = "".join(f'<th scope="col">{d}</th>' for d in DAYS)
    rows = []
    for slot in SLOTS:
        cells = []
        for d in range(5):
            items = by_time([s for s in SESSIONS if s["day"] == d and slot_of(s) == slot])
            cells.append("<td>" + ("<ul>" + "".join(item(s) for s in items) + "</ul>" if items else "") + "</td>")
        rows.append(f'<tr><th scope="row">{slot}</th>{"".join(cells)}</tr>')
    filters = "".join(f'<button type="button" class="filter f-{c["type"]}" data-class="{c["id"]}" aria-pressed="false">{e(c["name"])}</button>' for c in CLASSES)
    tabs, days = [], []
    for i, d in enumerate(DAYS):
        items = by_time([s for s in SESSIONS if s["day"] == i])
        tabs.append(f'<button type="button" class="tt-tab" role="tab" id="tt-t{i}" aria-controls="tt-p{i}" aria-selected="false" tabindex="-1"><b>{SHORT[i]}</b><span>{len(items)} clases</span></button>')
        days.append(f'<div class="tt-day" id="tt-p{i}" role="tabpanel" aria-labelledby="tt-t{i}"><h{heading_level}>{d}</h{heading_level}><ul>{"".join(item(s) for s in items)}</ul></div>')
    return f'''<div class="timetable" data-timetable>
<div class="filters" role="group" aria-label="Filtrar el horario por clase"><button type="button" class="filter" data-class="" aria-pressed="true">Todas</button>{filters}</div>
<p class="sr-only" aria-live="polite" data-filter-status></p>
<table class="tt"><caption class="sr-only">Horario semanal de clases, de lunes a viernes</caption>
<thead><tr><td></td>{head_row}</tr></thead><tbody>{"".join(rows)}</tbody></table>
<div class="tt-tabs" role="tablist" aria-label="Día de la semana">{"".join(tabs)}</div>
<div class="tt-days">{"".join(days)}</div>
</div>'''


def call_status():
    return '<p class="call-status" data-call-status></p>'


def calls_table():
    rows = "".join(f'<tr><th scope="row">{DAYS[c["day"]]}</th><td>{c["from"]}–{c["to"]}</td></tr>' for c in D["callHours"])
    return f'<table class="calls"><tbody>{rows}</tbody></table>'


def phone_block(p, title="Reserva tu plaza llamando"):
    """The one big pink area of a page (rule 2)."""
    return f'''<section class="phone-block" aria-labelledby="phone-title">
<div class="wrap phone-in">
<div>
<h2 id="phone-title" class="phone-title">{title}</h2>
<a class="phone-xl" href="{TEL}">{S["phone"]}</a>
{call_status()}
</div>
<div class="phone-side">
<h3 class="label">Horario de llamadas</h3>
{calls_table()}
<p>{ext(WHATSAPP, I_MSG + "Escribir por WhatsApp", "btn btn-on-pink")}</p>
</div>
</div>
</section>'''


def steps(p):
    return f'''<ol class="steps">
<li><b>Elige tu clase</b> en el <a href="{p}horario/">horario</a>, según tu nivel y tu semana.</li>
<li><b>Llámanos</b> o escríbenos: te decimos si hay plaza y te la reservamos.</li>
<li><b>Ven a clase</b> con ropa cómoda, agua y ganas.</li>
</ol>'''


def rating(cls="rating"):
    r = S["rating"]
    return f'<p class="{cls}">' + ext(S["reviewsUrl"], f'<b>{r["value"]}</b> <span class="stars" aria-hidden="true">★★★★★</span> {r["count"]} reseñas en Google') + "</p>"


def banner(p, key):
    return f'<figure class="wrap banner">{img(p, D["photos"][key], "banner-img", "(max-width: 860px) 100vw, 1200px")}</figure>'


def sec(num, ident, title, aside, body):
    return f'''<section class="sec wrap" id="{ident}" aria-labelledby="{ident}-title">
<div class="sec-label"><span class="sec-num">{num}</span><h2 id="{ident}-title">{title}</h2>{aside}</div>
<div class="sec-body">
{body}
</div>
</section>'''


def page_hero(num, title, lead, extra=""):
    n = f'<span class="sec-num">{num}</span>' if num else ""
    return f'''<section class="page-hero wrap">
{n}
<h1>{title}</h1>
<p class="lead">{lead}</p>
{extra}
</section>'''


# ---------- pages ----------
def page_home():
    p = ""
    nadia = D["photos"]["nadia"]
    return head(p, "", f'{S["name"]} · Baile y fitness en Torrox Costa',
                "Academia de baile y fitness en Torrox Costa (Málaga): grupos de dance por niveles para peques, jóvenes y adultos, Fitdance, PowerHIIT y Aquafitness, de lunes a viernes.") + header(p, "") + f'''<main id="main">
<section class="hero wrap">
<div class="hero-copy">
<h1>Baile y fitness para <em>peques</em>, jóvenes y adultos</h1>
<p class="lead">Grupos de dance por niveles, Fitdance, PowerHIIT y Aquafitness, de lunes a viernes en Urb. Santa Rosa, Torrox Costa. Plazas limitadas por grupo.</p>
<p class="hero-actions"><a class="btn-primary" href="{TEL}">{I_PHONE}Llamar al {S["phone"]}</a><a class="link-cta" href="horario/">Ver el horario <span aria-hidden="true">→</span></a></p>
</div>
{today_board(p)}
</section>
{banner(p, "outdoor1")}
{sec("01", "clases", "Clases", f'<p>{len(CLASSES)} clases, cada una con su grupo y su horario fijo.</p>{legend()}<p><a class="link-cta" href="clases/">Todas las clases <span aria-hidden="true">→</span></a></p>', class_lists(p))}
{sec("02", "horario", "Horario", f'<p>Curso {S["season"]}. Pulsa una clase para ver solo sus horas.</p><p><a class="link-cta" href="horario/">Horario completo <span aria-hidden="true">→</span></a></p>', timetable(p, 3))}
{sec("03", "nadia", "Nadia", "", f"""<div class="nadia">
{img(p, nadia, "nadia-photo", "(max-width: 860px) 100vw, 420px")}
<div>
<p class="big">Monitora de todos los grupos: dance por niveles, desde los más pequeños hasta adultos, y Fitdance, PowerHIIT y Aquafitness.</p>
{rating()}
<p><a class="link-cta" href="quien-soy/">Conoce a Nadia <span aria-hidden="true">→</span></a></p>
</div>
</div>""")}
{sec("04", "apuntate", "Apúntate", "", steps(p))}
{phone_block(p)}
</main>
''' + footer(p)


def page_classes():
    p = "../"
    return head(p, "clases/", "Clases de baile y fitness en Torrox Costa · Nadia Fitness",
                "Grupo Dance Baby, Intermedio, Avanzado y Adultos, Fitdance, PowerHIIT y Aquafitness en Torrox Costa: para quién es cada clase, qué se hace y en qué horario.") + header(p, "clases/") + f'''<main id="main">
{page_hero("01", f"{len(CLASSES)} clases de baile <em>y fitness</em>", "Cada clase tiene su grupo y su horario fijo de lunes a viernes. Para tarifas y plazas libres, llámanos.", legend())}
<section class="wrap cd-list" aria-label="Clases">
{class_lists(p, detail=True)}
</section>
{phone_block(p)}
</main>
''' + footer(p)


def page_schedule():
    p = "../"
    return head(p, "horario/", f'Horario curso {S["season"]} · {S["name"]}, Torrox Costa',
                f'Horario semanal de clases de baile y fitness en Torrox Costa, curso {S["season"]}, de lunes a viernes de {first_start()} a {last_end()}.',
                og="og-horario.jpg", og_alt="Horario semanal de clases de Nadia Fitness Dance Studio, de lunes a viernes") + header(p, "horario/") + f'''<main id="main">
<section class="page-hero page-hero-split wrap">
<div>
<span class="sec-num">02</span>
<h1>{len(SESSIONS)} clases <em>a la semana</em></h1>
<p class="lead">Curso {S["season"]}, de lunes a viernes de {first_start()} a {last_end()}. Plazas limitadas por grupo: llámanos para confirmar.</p>
{legend()}
<p class="print-row"><button type="button" class="btn print-btn" data-print>{I_PRINT}Imprimir horario</button></p>
</div>
{today_board(p)}
</section>
<section class="wrap sec-plain" aria-labelledby="week-title">
<h2 id="week-title" class="sr-only">Horario semanal</h2>
<p class="print-only">{e(S["name"])} · {e(S["street"])}, {S["postalCode"]} {e(S["locality"])} · Tel. {S["phone"]} · Curso {S["season"]}</p>
{timetable(p)}
</section>
{phone_block(p)}
</main>
''' + footer(p)


def page_about():
    p = "../"
    nadia = D["photos"]["nadia"]
    teach = "".join(f'<li><a href="{p}clases/#{c["id"]}">{e(c["name"])}</a><span>{e(kind_label(c))}</span></li>' for c in CLASSES)
    return head(p, "quien-soy/", "Quién soy · Nadia, monitora de baile y fitness en Torrox Costa",
                "Nadia, monitora de Nadia Fitness Dance Studio en Torrox Costa: grupos de dance por niveles, Fitdance, PowerHIIT y Aquafitness.") + header(p, "quien-soy/") + f'''<main id="main">
{page_hero("03", "Hola, soy <em>Nadia</em>", "Monitora de baile y fitness en Torrox Costa.")}
<section class="wrap sec-plain">
<div class="nadia">
{img(p, nadia, "nadia-photo", "(max-width: 860px) 100vw, 420px", eager=True)}
<div>
<!-- TODO: replace with Nadia's own words (background, training, years teaching) -->
<p class="big">Soy la monitora de Nadia Fitness Dance Studio, en Torrox Costa. Doy clase a los grupos de dance por niveles, desde los más pequeños hasta adultos, y a Fitdance, PowerHIIT y Aquafitness.</p>
<p>En mis clases cada persona avanza a su ritmo: aprendemos técnica y coreografía, entrenamos en serio y lo pasamos bien. Si nunca has bailado, te ayudo a encontrar tu grupo.</p>
{rating()}
<h2 class="label nadia-sub">Las clases que doy</h2>
<ul class="plain-list">{teach}</ul>
</div>
</div>
</section>
{banner(p, "outdoor2")}
{phone_block(p)}
</main>
''' + footer(p)


def page_contact():
    p = "../"
    options = "".join(f'<option value="{c["id"]}">{e(c["name"])}</option>' for c in CLASSES) + '<option value="">Aún no lo sé</option>'
    return head(p, "contacto/", f'Contacto y reservas · {S["name"]}, Torrox Costa',
                "Reserva tu plaza en Nadia Fitness Dance Studio, Torrox Costa: teléfono y horario de llamadas, WhatsApp, dirección y mapa.") + header(p, "contacto/") + f'''<main id="main">
{page_hero("04", "Reserva <em>tu plaza</em>", "Llámanos en horario de llamadas o escríbenos por WhatsApp: te decimos si queda plaza en el grupo y te la guardamos.")}
{phone_block(p, "Llámanos")}
<section class="wrap sec-plain contact" aria-label="Escribir y cómo llegar">
<form class="form" id="contact-form" novalidate>
<h2 class="form-title">Escríbenos por WhatsApp</h2>
<div class="field"><label for="contact-name">Nombre</label><input id="contact-name" name="contact-name" autocomplete="name" required placeholder="Tu nombre" aria-describedby="contact-name-error"><p class="field-error" id="contact-name-error" role="alert" hidden>Escribe tu nombre para que sepamos quién eres.</p></div>
<div class="field"><label for="contact-phone">Teléfono <span class="opt">(opcional)</span></label><input id="contact-phone" name="contact-phone" type="tel" autocomplete="tel" placeholder="+34"></div>
<div class="field"><label for="contact-class">Clase que te interesa</label><select id="contact-class" name="contact-class">{options}</select></div>
<div class="field"><label for="contact-message">Mensaje <span class="opt">(opcional)</span></label><textarea id="contact-message" name="contact-message" rows="3" placeholder="Edad, nivel, dudas…"></textarea></div>
<button class="btn" type="submit">{I_MSG}Abrir WhatsApp con el mensaje</button>
<p class="note">No guardamos ningún dato: el mensaje solo se envía si lo mandas tú desde WhatsApp. Sin JavaScript, usa el botón de WhatsApp de arriba.</p>
</form>
<div class="where">
<h2 class="form-title">Dónde estamos</h2>
<address>{e(S["street"])}<br>{S["postalCode"]} {e(S["locality"])}, {e(S["region"])}</address>
<figure class="map"><a href="{e(S["mapsUrl"])}" target="_blank" rel="noopener"><img src="../assets/img/mapa.webp" alt="Mapa de Urb. Santa Rosa con la academia en la Calle Margarita" width="1280" height="720" loading="lazy"><span class="map-pin" aria-hidden="true"></span><span class="map-go">Cómo llegar →</span>{NEW_TAB}</a><figcaption>© <a href="https://www.openstreetmap.org/copyright" rel="noopener">OpenStreetMap</a></figcaption></figure>
{steps(p)}
</div>
</section>
</main>
''' + footer(p)


def legal_body(slug):
    b = D["legal"][slug]["body"]
    labels = {"name": "Nombre completo de la titular o razón social", "nif": "NIF / DNI", "email": "Email de contacto"}
    for k, lab in labels.items():
        v = D["owner"].get(k)
        b = b.replace(f'<mark class="ph-mark">[{lab}]</mark>', e(v) if v else f'<mark class="ph-mark">[{lab}]</mark>')
    addr = f'{S["street"]}, {S["postalCode"]} {S["locality"]} ({S["region"]})'
    b = b.replace("Urb. Santa Rosa, Calle Margarita 6, 29793 Torrox Costa (Málaga)", e(addr))
    b = b.replace('<a href="tel:+34654691336">654 691 336</a>', f'<a href="{TEL}">{S["phone"]}</a>')
    import re
    b = re.sub(r"Última actualización: [^<]+?\.", f'Última actualización: {D["legalUpdated"]}.', b)
    return b


def page_legal(slug):
    p = "../"
    L = D["legal"][slug]
    back = '<p class="back"><a class="back-link" href="../" data-back><span aria-hidden="true">←</span> Volver</a></p>'
    return head(p, f"{slug}/", L["title"], L["lead"]) + header(p, None) + f'''<main id="main">
<section class="page-hero wrap">
{back}
<h1>{e(L["h1"])}</h1>
<p class="lead">{e(L["lead"])}</p>
</section>
<section class="wrap sec-plain prose">
{legal_body(slug)}
{back.replace('class="back"', 'class="back back-end"')}
</section>
</main>
''' + footer(p)


def page_404():
    p = SITE_PATH
    links = "".join(f'<li><a href="{p}{h}">{l}</a><span>{d}</span></li>' for h, l, d in (
        ("horario/", "Horario de clases", "Qué hay cada día"), ("clases/", "Clases", "Para quién es cada una"),
        ("contacto/", "Contacto", "Teléfono, WhatsApp y mapa"), ("", "Inicio", "Página principal")))
    return head(p, None, f'Página no encontrada · {S["name"]}', "Esta página no existe.") + header(p, None) + f'''<main id="main">
{page_hero("404", "Este paso <em>no existe</em>", "Puede que el enlace esté mal o que la página se haya movido.")}
<section class="wrap sec-plain"><ul class="plain-list notfound">{links}</ul></section>
</main>
''' + footer(p)


# ---------- other generated files ----------
def sitemap():
    urls = "".join(f"  <url><loc>{SITE}{p}</loc><lastmod>2026-11-17</lastmod></url>\n"
                   for p in ("", "clases/", "horario/", "quien-soy/", "contacto/", "aviso-legal/", "privacidad/"))
    return f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{urls}</urlset>\n'


def manifest():
    return json.dumps({"name": S["name"], "short_name": "Nadia Fitness", "description": S["tagline"] + ".",
                       "lang": "es", "start_url": "./", "scope": "./", "display": "browser",
                       "background_color": "#F4EFE8", "theme_color": "#16120F",
                       "icons": [{"src": "assets/img/icon-192.png", "sizes": "192x192", "type": "image/png"},
                                 {"src": "assets/img/icon-512.png", "sizes": "512x512", "type": "image/png"}]},
                      ensure_ascii=False, indent=2) + "\n"


def images():
    """Class placeholders and the timetable share image, drawn from the data (needs Pillow)."""
    from PIL import Image, ImageDraw, ImageFont
    display = os.path.join(ROOT, "assets/fonts/barlow-condensed-800-normal-latin.woff2")
    text = os.path.join(ROOT, "assets/fonts/instrument-sans-normal-latin.woff2")

    def sans(size, weight=600):
        f = ImageFont.truetype(text, size)
        try:
            f.set_variation_by_axes([weight] + [a["default"] for a in f.get_variation_axes()[1:]])
        except Exception:
            pass
        return f

    paper, ink, muted, pink, rule = (236, 229, 219), (22, 18, 15), (94, 85, 77), (194, 0, 106), (200, 191, 179)
    for i, c in enumerate(CLASSES, 1):
        if not c["placeholder"]:
            continue
        im = Image.new("RGB", (1200, 750), paper)
        d = ImageDraw.Draw(im)
        d.line((60, 90, 1140, 90), fill=ink, width=4)
        d.text((60, 112), f"{i:02d}", font=sans(30), fill=muted)
        lab = kind_label(c).upper()
        d.text((1140 - d.textlength(lab, font=sans(28)), 112), lab, font=sans(28), fill=muted)
        title = ImageFont.truetype(display, 132 if len(c["name"]) < 16 else 110)
        words, lines, cur = c["name"].upper().split(), [], ""
        for w in words:
            t = (cur + " " + w).strip()
            if d.textlength(t, font=title) > 1080 and cur:
                lines.append(cur); cur = w
            else:
                cur = t
        lines.append(cur)
        y = 750 - 150 - len(lines) * title.size * 1.08
        for line in lines:
            d.text((60, y), line, font=title, fill=ink)
            y += title.size * 1.08
        d.rectangle((60, 640, 220, 646), fill=pink)
        d.line((60, 690, 1140, 690), fill=rule, width=2)
        im.save(os.path.join(ROOT, "assets/img", c["photo"]), "WEBP", quality=86, method=6)

    # timetable share image (1200x630)
    im = Image.new("RGB", (1200, 630), (22, 18, 15))
    d = ImageDraw.Draw(im)
    logo = Image.open(os.path.join(ROOT, "assets/img/logo.png")).convert("RGBA")
    logo = logo.resize((150, round(logo.height * 150 / logo.width)), Image.LANCZOS)
    im.paste(logo, (990, 40), logo)
    d.text((60, 36), f'HORARIO CURSO {S["season"]}', font=ImageFont.truetype(display, 70), fill=(243, 238, 230))
    d.text((60, 122), f'{S["name"]} · {S["locality"]} · Tel. {S["phone"]}', font=sans(24, 500), fill=(168, 158, 147))
    colw = 1080 / 5
    for i, day in enumerate(DAYS):
        x = 60 + i * colw
        d.text((x, 186), day.upper(), font=ImageFont.truetype(display, 34), fill=(243, 238, 230))
        d.line((x, 232, x + colw - 16, 232), fill=(243, 238, 230), width=2)
        y = 246
        for s in by_time([s for s in SESSIONS if s["day"] == i]):
            dance = BY_ID[s["class"]]["type"] == "dance"
            if dance:
                d.rectangle((x, y + 2, x + 3, y + 46), fill=(255, 90, 168))
            else:
                for yy in range(y + 2, y + 46, 8):
                    d.rectangle((x, yy, x + 3, yy + 4), fill=(243, 238, 230))
            d.text((x + 12, y), f'{s["start"]}–{s["end"]}', font=sans(17, 500), fill=(168, 158, 147))
            d.text((x + 12, y + 22), name_of(s).replace("Grupo ", ""), font=sans(19, 650), fill=(243, 238, 230))
            y += 64
    im.save(os.path.join(ROOT, "assets/img/og-horario.jpg"), "JPEG", quality=86, optimize=True, progressive=True)


def write(rel, content):
    path = os.path.join(ROOT, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print("wrote", rel)


if __name__ == "__main__":
    write("index.html", page_home())
    write("clases/index.html", page_classes())
    write("horario/index.html", page_schedule())
    write("quien-soy/index.html", page_about())
    write("contacto/index.html", page_contact())
    write("aviso-legal/index.html", page_legal("aviso-legal"))
    write("privacidad/index.html", page_legal("privacidad"))
    write("404.html", page_404())
    write("sitemap.xml", sitemap())
    write("robots.txt", f"User-agent: *\nAllow: /\n\nSitemap: {SITE}sitemap.xml\n")
    write("site.webmanifest", manifest())
    write(".nojekyll", "")
    images()
    print("images: class placeholders + og-horario.jpg")
