#!/usr/bin/env python3
"""Generate the personality detail pages and the listing cards.

Source of truth: content/figures.json (one record per personality).

Outputs:
  - personnalites/<id>.html   — one full detail page per figure
  - personnalites.html        — the cards between <!-- figures:start --> and
                                <!-- figures:end --> markers

Run after editing content/figures.json:
    python3 tools/build_figures.py

tools/validate.py fails when the generated output is stale.
"""
import html
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FIGURES = ROOT / "content" / "figures.json"
OUT_DIR = ROOT / "personnalites"
LISTING = ROOT / "personnalites.html"

NAV = [
    ("index", "index.html", "Accueil"),
    ("histoire", "histoire.html", "Histoire"),
    ("culture", "culture.html", "Culture"),
    ("villes", "villes.html", "Villes &amp; territoire"),
    ("personnalites", "personnalites.html", "Personnalités"),
    ("galerie", "galerie.html", "Galerie"),
    ("contact", "contact.html", "Contact"),
]

FONTS = (
    '<link rel="preconnect" href="https://fonts.googleapis.com">\n'
    '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
    '<link href="https://fonts.googleapis.com/css2?family=Amiri:ital,wght@0,400;0,700;1,400&family=Cormorant+Garamond:ital,wght@0,500;0,600;0,700;1,500&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">'
)


def esc(s: str) -> str:
    return html.escape(s, quote=True)


def strip_tags(s: str) -> str:
    return re.sub(r"<[^>]+>", "", s)


def head(title: str, description: str, css: str) -> str:
    return (
        "<!DOCTYPE html>\n"
        '<html lang="fr">\n'
        "<head>\n"
        '<meta charset="UTF-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1.0">\n'
        f"<title>{title}</title>\n"
        f'<meta name="description" content="{description}">\n'
        f"{FONTS}\n"
        f'<link rel="stylesheet" href="{css}">\n'
        "</head>\n"
    )


def nav(prefix: str) -> str:
    items = "\n".join(
        f'      <li><a href="{prefix}{href}" data-nav="{key}">{label}</a></li>'
        for key, href, label in NAV
    )
    return (
        '<header class="site-header">\n'
        '  <nav class="nav container" aria-label="Navigation principale">\n'
        f'    <a class="brand" href="{prefix}index.html">\n'
        '      <span class="brand-mark">ⵜⵙ</span>\n'
        '      <span class="brand-text">Souss <em>ⵜⴰⵎⴰⵣⵉⵔⵜ ⵏ ⵙⵓⵙ</em></span>\n'
        "    </a>\n"
        '    <button class="nav-toggle" id="navToggle" aria-label="Ouvrir le menu" aria-expanded="false">\n'
        "      <span></span><span></span><span></span>\n"
        "    </button>\n"
        '    <ul class="nav-links" id="navLinks">\n'
        f"{items}\n"
        "    </ul>\n"
        "  </nav>\n"
        "</header>\n"
    )


def footer(prefix: str) -> str:
    links = "\n".join(
        f'      <a href="{prefix}{href}">{label}</a>' for _, href, label in NAV
    )
    return (
        '<footer class="site-footer">\n'
        '  <div class="container footer-inner">\n'
        '    <div class="footer-brand">\n'
        '      <span class="brand-mark">ⵜⵙ</span>\n'
        "      <div>\n"
        "        <strong>Souss — ⊔ⴰⵎⴰⵣⵉⵔⵜ ⵏ ⵙⵓⵙ</strong>\n"
        "        <p>Site hommage à la région du Souss : son histoire, sa culture amazighe, ses villes et ses grandes personnalités.</p>\n"
        "      </div>\n"
        "    </div>\n"
        '    <nav class="footer-nav" aria-label="Pied de page">\n'
        f"{links}\n"
        "    </nav>\n"
        '    <p class="footer-note">Sources : Wikipédia (Mohamed Mokhtar Soussi, Ali Azaykou, Mohammed Khaïr-Eddine, Ahmed Adghirni, Lhaj Belaid, Ammouri M\'Barek, Ali Chouhad, Abdallah ibn Yassin, Ibn Tumert, el-Hajj Ahmed el-Jachymi, Sidi Ahmed Ou Moussa, Ahmed al-Hiba…), Arrabita.ma (Ahmed al-Kachti al-Tinani), Wikimedia Commons. Contenu indicatif.</p>\n'
        "  </div>\n"
        "</footer>\n"
        "\n"
        f'<script src="{prefix}app.js"></script>\n'
        "</body>\n"
        "</html>\n"
    )


def img_attrs(fig: dict, prefix: str) -> str:
    img = fig["image"]
    src = img["src"]
    if not src.startswith(("http://", "https://")):
        src = prefix + src
    out = f'<img src="{esc(src)}" alt="{esc(img["alt"])}" loading="lazy"'
    if img.get("referrerpolicy"):
        out += ' referrerpolicy="no-referrer"'
    return out + ">"


def render_card(fig: dict) -> str:
    cats = " ".join(fig["cats"])
    works = (
        f'\n            <p class="person-works"><strong>Œuvres marquantes :</strong> {fig["works"]}</p>'
        if fig.get("works")
        else ""
    )
    return (
        f'        <article class="person reveal" id="{esc(fig["id"])}" data-cat="{esc(cats)}">\n'
        f'          <div class="person-photo has-img">{img_attrs(fig, "")}'
        f'<span class="person-initials">{esc(fig["initials"])}</span>'
        f'<span class="photo-credit">{esc(fig["image"]["credit"])}</span></div>\n'
        '          <div class="person-body">\n'
        f'            <h3><a class="person-name" href="personnalites/{esc(fig["id"])}.html">{esc(fig["name"])}</a>'
        f' <span class="person-tag">{esc(fig["tag"])}</span></h3>\n'
        f'            <p class="person-meta">{esc(fig["meta"])}</p>\n'
        f"            <p>{fig['teaser']}</p>{works}\n"
        f'            <p class="person-cta"><a class="btn btn-ghost btn-sm" href="personnalites/{esc(fig["id"])}.html">Fiche complète →</a></p>\n'
        "          </div>\n"
        "        </article>\n"
    )


def render_detail(fig: dict, all_figs: list) -> str:
    prefix = "../"
    facts = "\n".join(
        f"          <div><dt>{k}</dt><dd>{v}</dd></div>"
        for k, v in fig.get("facts", [])
    )
    bio = "\n".join(f"        <p>{p}</p>" for p in fig["bio"])
    works = (
        f'\n        <h2>Œuvres marquantes</h2>\n        <p class="profile-works">{fig["works"]}</p>'
        if fig.get("works")
        else ""
    )
    timeline = "\n".join(
        f'          <li><span class="profile-year">{y}</span><span>{t}</span></li>'
        for y, t in fig.get("timeline", [])
    )
    sources = "\n".join(
        f'          <li><a href="{esc(s["url"])}" target="_blank" rel="noopener">{esc(s["label"])}</a></li>'
        for s in fig.get("sources", [])
    )
    # related: other figures sharing a category, up to 3
    related_ids = [
        f["id"]
        for f in all_figs
        if f["id"] != fig["id"] and set(f["cats"]) & set(fig["cats"])
    ][:3]
    related = "\n".join(
        f'          <a class="related-card reveal" href="{esc(rid)}.html">'
        f'<strong>{esc(next(f["name"] for f in all_figs if f["id"] == rid))}</strong>'
        f'<span>{esc(next(f["tag"] for f in all_figs if f["id"] == rid))}</span></a>'
        for rid in related_ids
    )
    related_block = (
        '\n      <h2 class="related-title">À lire aussi</h2>\n'
        '      <div class="related-grid">\n'
        f"{related}\n"
        "      </div>"
        if related
        else ""
    )

    return (
        head(
            f"{esc(fig['name'])} — Personnalités du Souss",
            esc(strip_tags(fig["teaser"]))[:170],
            prefix + "style.css",
        )
        + '<body data-page="personnalites">\n'
        + nav(prefix)
        + "\n<main>\n\n"
        "  <section class=\"page-hero\">\n"
        "    <div class=\"container\">\n"
        '      <p class="section-kicker reveal">04 — Grandes voix</p>\n'
        f"      <h1 class=\"reveal\">{esc(fig['name'])}</h1>\n"
        f'      <p class="section-intro reveal"><span class="person-tag">{esc(fig["tag"])}</span></p>\n'
        f'      <p class="person-meta reveal">{esc(fig["meta"])}</p>\n'
        f'      <p class="reveal"><a class="back-link" href="../personnalites.html">← Toutes les personnalités</a></p>\n'
        "    </div>\n"
        "  </section>\n\n"
        '  <section class="section">\n'
        '    <div class="container">\n'
        '      <div class="profile">\n'
        '        <aside class="profile-side reveal">\n'
        f'          <div class="person-photo has-img profile-photo">{img_attrs(fig, prefix)}'
        f'<span class="photo-credit">{esc(fig["image"]["credit"])}</span></div>\n'
        '          <dl class="profile-facts">\n'
        f"{facts}\n"
        "          </dl>\n"
        "        </aside>\n"
        '        <div class="profile-body reveal">\n'
        "          <h2>Biographie</h2>\n"
        f"{bio}{works}\n"
        "          <h2>Repères</h2>\n"
        '          <ul class="profile-timeline">\n'
        f"{timeline}\n"
        "          </ul>\n"
        "          <h2>Sources</h2>\n"
        '          <ul class="profile-sources">\n'
        f"{sources}\n"
        "          </ul>\n"
        f"{related_block}\n"
        "        </div>\n"
        "      </div>\n"
        "    </div>\n"
        "  </section>\n\n"
        "</main>\n\n"
        + footer(prefix)
    )


def render_listing_block(figs: list) -> str:
    return "".join(render_card(f) for f in figs)


def listing_mid(figs: list) -> str:
    """Exact text that must sit between the figures markers in personnalites.html."""
    return "\n" + render_listing_block(figs) + "        "


def build() -> list[str]:
    figs = json.loads(FIGURES.read_text(encoding="utf-8"))
    problems = []
    ids = [f["id"] for f in figs]
    if len(ids) != len(set(ids)):
        problems.append("duplicate ids in figures.json")

    OUT_DIR.mkdir(exist_ok=True)
    for f in figs:
        page = OUT_DIR / f"{f['id']}.html"
        page.write_text(render_detail(f, figs), encoding="utf-8")

    # rewrite the listing between markers
    text = LISTING.read_text(encoding="utf-8")
    m = re.search(
        r"(<!-- figures:start -->)(.*?)(<!-- figures:end -->)",
        text,
        flags=re.S,
    )
    if not m:
        problems.append("personnalites.html: figures markers not found")
    else:
        text = text[: m.start(2)] + listing_mid(figs) + text[m.end(2):]
        LISTING.write_text(text, encoding="utf-8")
    return problems


if __name__ == "__main__":
    errors = build()
    if errors:
        print("BUILD FAILED:")
        for e in errors:
            print(" -", e)
        sys.exit(1)
    print("BUILD OK — personnalites/*.html + personnalites.html cards regenerated")
