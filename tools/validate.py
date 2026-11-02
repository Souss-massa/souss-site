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
    for f in sorted(ROOT.glob("*.html")):
        c = BalanceChecker()
        c.feed(f.read_text(encoding="utf-8"))
        left = [t for t in c.stack if t not in ("html", "body")]
        if left:
            errors.append(f"{f.name}: unclosed tags {left}")


def check_links():
    for f in sorted(ROOT.glob("*.html")):
        text = f.read_text(encoding="utf-8")
        for m in re.finditer(r'(?:href|src)="([^"#]+)"', text):
            url = m.group(1)
            if url.startswith(("http://", "https://", "mailto:", "//")):
                continue
            target = (ROOT / url.split("#")[0].split("?")[0])
            if not target.exists():
                errors.append(f"{f.name}: broken internal link {url}")


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


if __name__ == "__main__":
    check_html()
    check_links()
    check_json_content()
    if errors:
        print("VALIDATION FAILED:")
        for e in errors:
            print(" -", e)
        sys.exit(1)
    print("VALIDATION OK")
