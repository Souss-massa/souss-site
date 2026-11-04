#!/usr/bin/env python3
"""Validate the Souss site content before merge.

Checks:
  1. HTML tag balance for every *.html page (excluding void elements).
  2. Internal links (href/src pointing to local files) resolve to existing files.
  3. content/*.json parse as JSON.
  4. content/personnalites.json entries match the schema (required fields,
     unique ids, allowed categories) and their image URLs answer HTTP 200.

Exit code 0 = valid, 1 = errors found (printed to stdout).
"""
import json
import re
import sys
import urllib.request
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input",
        "link", "meta", "source", "track", "wbr"}
ALLOWED_CATS = {"lettres", "musique", "spirituel", "resistance", "sport"}
REQUIRED = {"id", "name", "tag", "meta", "bio", "cats", "initials"}

errors: list[str] = []


class BalanceChecker(HTMLParser):
    def __init__(self):
        super().__init__()
        self.stack = []

    def handle_starttag(self, tag, attrs):
        if tag not in VOID:
            self.stack.append(tag)

    def handle_endtag(self, tag):
        if tag in VOID:
            return
        if self.stack and self.stack[-1] == tag:
            self.stack.pop()
        else:
            errors.append(f"HTML mismatch: </{tag}> at line {self.getpos()[0]}")


def check_html():
    for f in sorted(ROOT.rglob("*.html")):
        if ".git" in f.parts:
            continue
        c = BalanceChecker()
        c.feed(f.read_text(encoding="utf-8"))
        left = [t for t in c.stack if t not in ("html", "body")]
        if left:
            errors.append(f"{f.relative_to(ROOT)}: unclosed tags {left}")


def check_links():
    for f in sorted(ROOT.rglob("*.html")):
        if ".git" in f.parts:
            continue
        text = f.read_text(encoding="utf-8")
        for m in re.finditer(r'(?:href|src)="([^"#]+)"', text):
            url = m.group(1)
            if url.startswith(("http://", "https://", "mailto:", "//")):
                continue
            target = (f.parent / url.split("#")[0].split("?")[0]).resolve()
            if not target.exists():
                errors.append(f"{f.relative_to(ROOT)}: broken internal link {url}")


def check_json_content():
    cdir = ROOT / "content"
    for f in sorted(cdir.glob("*.json")):
        try:
            json.loads(f.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            errors.append(f"content/{f.name}: invalid JSON: {e}")
    pfile = cdir / "personnalites.json"
    if not pfile.exists():
        errors.append("content/personnalites.json missing")
        return
    data = json.loads(pfile.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        errors.append("content/personnalites.json must be a JSON array")
        return
    seen = set()
    for i, p in enumerate(data):
        where = f"personnalites.json[{i}]"
        missing = REQUIRED - set(p)
        if missing:
            errors.append(f"{where}: missing fields {sorted(missing)}")
        if p.get("id") in seen:
            errors.append(f"{where}: duplicate id {p.get('id')!r}")
        seen.add(p.get("id"))
        bad = set(p.get("cats", [])) - ALLOWED_CATS
        if bad:
            errors.append(f"{where}: unknown cats {sorted(bad)}")
        img = p.get("image")
        if img and isinstance(img, dict) and img.get("src", "").startswith("http"):
            req = urllib.request.Request(img["src"], method="HEAD",
                                         headers={"User-Agent": "souss-site-ci/1.0"})
            try:
                with urllib.request.urlopen(req, timeout=20) as r:
                    if r.status != 200:
                        errors.append(f"{where}: image HTTP {r.status}: {img['src']}")
            except Exception as e:
                errors.append(f"{where}: image unreachable: {img['src']} ({e})")


FIGURE_REQUIRED = {"id", "name", "tag", "meta", "cats", "initials", "image",
                   "teaser", "bio", "sources"}


def check_figures():
    """content/figures.json schema + generated pages up to date."""
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import build_figures

    ffile = ROOT / "content" / "figures.json"
    if not ffile.exists():
        errors.append("content/figures.json missing")
        return
    figs = json.loads(ffile.read_text(encoding="utf-8"))
    if not isinstance(figs, list) or not figs:
        errors.append("content/figures.json must be a non-empty JSON array")
        return
    seen = set()
    for i, fig in enumerate(figs):
        where = f"figures.json[{i}]"
        missing = FIGURE_REQUIRED - set(fig)
        if missing:
            errors.append(f"{where}: missing fields {sorted(missing)}")
        if fig.get("id") in seen:
            errors.append(f"{where}: duplicate id {fig.get('id')!r}")
        seen.add(fig.get("id"))
        bad = set(fig.get("cats", [])) - ALLOWED_CATS
        if bad:
            errors.append(f"{where}: unknown cats {sorted(bad)}")
        if not fig.get("bio"):
            errors.append(f"{where}: empty bio")
        img = fig.get("image")
        if isinstance(img, dict):
            src = img.get("src", "")
            if not src.startswith(("http://", "https://")):
                if not (ROOT / src).exists():
                    errors.append(f"{where}: local image missing: {src}")
            for field in ("alt", "credit"):
                if not img.get(field):
                    errors.append(f"{where}: image.{field} missing")

    # generated output up to date?
    for fig in figs:
        page = ROOT / "personnalites" / f"{fig['id']}.html"
        want = build_figures.render_detail(fig, figs)
        if not page.exists():
            errors.append(f"{page.relative_to(ROOT)}: missing; run python3 tools/build_figures.py")
        elif page.read_text(encoding="utf-8") != want:
            errors.append(f"{page.relative_to(ROOT)}: stale; run python3 tools/build_figures.py")
    text = (ROOT / "personnalites.html").read_text(encoding="utf-8")
    m = re.search(r"<!-- figures:start -->(.*?)<!-- figures:end -->", text, flags=re.S)
    if not m:
        errors.append("personnalites.html: figures markers not found")
    elif m.group(1) != build_figures.listing_mid(figs):
        errors.append("personnalites.html: figures cards stale; run python3 tools/build_figures.py")


if __name__ == "__main__":
    check_html()
    check_links()
    check_json_content()
    check_figures()
    if errors:
        print("VALIDATION FAILED:")
        for e in errors:
            print(" -", e)
        sys.exit(1)
    print("VALIDATION OK")
