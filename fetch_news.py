#!/usr/bin/env python3
"""
Henter nyheter fra alle RSS-kildene i docs/sources.json og skriver dem
til docs/news.json. Kjøres daglig av GitHub Actions (se .github/workflows/update-news.yml),
men kan også kjøres manuelt lokalt: python scripts/fetch_news.py
"""
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

import feedparser

ROOT = Path(__file__).resolve().parent.parent
SOURCES_PATH = ROOT / "docs" / "sources.json"
OUTPUT_PATH = ROOT / "docs" / "news.json"

MAX_ITEMS_PER_SOURCE = 25
MAX_TOTAL_ITEMS = 400
INGRESS_MAX_LENGTH = 220


def strip_html(raw_html: str) -> str:
    if not raw_html:
        return ""
    text = re.sub(r"<[^>]+>", " ", raw_html)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def make_ingress(text: str) -> str:
    text = strip_html(text)
    if len(text) > INGRESS_MAX_LENGTH:
        text = text[:INGRESS_MAX_LENGTH].rsplit(" ", 1)[0] + "…"
    return text


def fnv1a(text: str) -> str:
    """FNV-1a 32-bit hash. Implemented identically in docs/index.html (JS) so
    that an article gets the SAME id whether it's fetched by this daily script
    or re-fetched live in the browser via the 'Oppdater nå' button — that way
    a hidden article stays hidden after a manual refresh."""
    h = 0x811C9DC5
    for byte in text.encode("utf-8"):
        h ^= byte
        h = (h * 0x01000193) & 0xFFFFFFFF
    return format(h, "08x")


def make_id(link: str, title: str) -> str:
    return fnv1a(f"{link}|{title}")


def parse_date(entry) -> str:
    for key in ("published_parsed", "updated_parsed"):
        val = getattr(entry, key, None)
        if val:
            try:
                return datetime(*val[:6], tzinfo=timezone.utc).isoformat()
            except Exception:
                pass
    return datetime.now(timezone.utc).isoformat()


def fetch_source(source: dict) -> list[dict]:
    name = source.get("name", "Ukjent kilde")
    url = source.get("url", "")
    category = source.get("category", "annet")

    if not url:
        return []

    try:
        parsed = feedparser.parse(url)
    except Exception as exc:  # noqa: BLE001
        print(f"[FEIL] Klarte ikke hente '{name}' ({url}): {exc}", file=sys.stderr)
        return []

    if parsed.bozo and not parsed.entries:
        print(f"[ADVARSEL] '{name}' ({url}) ga ingen gyldige oppføringer", file=sys.stderr)
        return []

    items = []
    for entry in parsed.entries[:MAX_ITEMS_PER_SOURCE]:
        link = entry.get("link", "")
        title = entry.get("title", "").strip()
        if not link or not title:
            continue
        summary = entry.get("summary", "") or entry.get("description", "")
        items.append(
            {
                "id": make_id(link, title),
                "title": title,
                "ingress": make_ingress(summary),
                "link": link,
                "source": name,
                "category": category,
                "published": parse_date(entry),
            }
        )
    return items


def main() -> None:
    if not SOURCES_PATH.exists():
        print(f"Fant ikke {SOURCES_PATH}", file=sys.stderr)
        sys.exit(1)

    sources = json.loads(SOURCES_PATH.read_text(encoding="utf-8"))

    all_items = []
    seen_ids = set()

    for source in sources:
        items = fetch_source(source)
        print(f"{source.get('name')}: {len(items)} saker")
        for item in items:
            if item["id"] in seen_ids:
                continue
            seen_ids.add(item["id"])
            all_items.append(item)

    all_items.sort(key=lambda x: x["published"], reverse=True)
    all_items = all_items[:MAX_TOTAL_ITEMS]

    output = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "items": all_items,
    }

    OUTPUT_PATH.write_text(
        json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"\nSkrev {len(all_items)} saker til {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
