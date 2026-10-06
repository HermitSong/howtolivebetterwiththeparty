#!/usr/bin/env python3
"""Search and validate the bundled source metadata; never fetch remote content."""
import argparse
from collections import Counter
from datetime import date
import json
from pathlib import Path
import re
import sys
from urllib.parse import urlparse

CATALOG = Path(__file__).resolve().parents[1] / "references" / "source-catalog.json"
TYPES = {"theory", "history", "party_document", "law", "policy", "statistics", "portal"}
STATES = {"opened_fulltext", "opened_portal", "search_only", "blocked"}
FIELDS = {"id", "title", "url", "publisher", "original_author", "event_date",
          "published_date", "checked_date", "doc_type", "period", "tags",
          "verification", "notes"}


def emit(value):
    # Keep Chinese metadata readable while avoiding legacy Windows encodings.
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    print(json.dumps(value, ensure_ascii=False, indent=2))


def validate(catalog):
    errors = []
    if not isinstance(catalog, dict):
        return ["Catalog must be an object"]
    if catalog.get("schema_version") != 1:
        errors.append("Unsupported schema_version")
    try:
        compiled = date.fromisoformat(catalog["compiled_on"])
    except (KeyError, TypeError, ValueError):
        return errors + ["compiled_on must be an ISO date"]
    if not isinstance(catalog.get("scope"), str) or not catalog["scope"].strip():
        errors.append("scope must describe the collection limits")
    sources = catalog.get("sources")
    if not isinstance(sources, list):
        return errors + ["sources must be an array"]
    seen_ids, seen_urls = set(), set()
    for index, item in enumerate(sources):
        key = f"sources[{index}]"
        if not isinstance(item, dict):
            errors.append(f"{key}: must be an object")
            continue
        missing = FIELDS - item.keys()
        if missing:
            errors.append(f"{key}: missing {sorted(missing)}")
            continue
        for field in FIELDS - {"event_date", "published_date", "tags"}:
            if not isinstance(item[field], str) or not item[field].strip():
                errors.append(f"{key}: {field} must be a nonempty string")
        source_id = item["id"]
        if not isinstance(source_id, str) or not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", source_id):
            errors.append(f"{key}: invalid id")
        elif source_id in seen_ids:
            errors.append(f"{key}: duplicate id {source_id}")
        else:
            seen_ids.add(source_id)
        url = item["url"]
        if not isinstance(url, str) or urlparse(url).scheme not in {"https", "http"} or not urlparse(url).netloc:
            errors.append(f"{key}: invalid source URL")
        elif url in seen_urls:
            errors.append(f"{key}: duplicate URL {url}")
        else:
            seen_urls.add(url)
        if not isinstance(item["doc_type"], str) or item["doc_type"] not in TYPES:
            errors.append(f"{key}: invalid doc_type")
        if not isinstance(item["verification"], str) or item["verification"] not in STATES:
            errors.append(f"{key}: invalid verification")
        if not isinstance(item["tags"], list) or not item["tags"] or not all(isinstance(t, str) and t.strip() for t in item["tags"]):
            errors.append(f"{key}: tags must be nonempty strings")
        parsed_dates = {}
        for field in ("event_date", "published_date", "checked_date"):
            raw = item[field]
            if raw is None and field != "checked_date":
                continue
            try:
                parsed_dates[field] = date.fromisoformat(raw)
            except (TypeError, ValueError):
                errors.append(f"{key}: invalid {field}")
        checked = parsed_dates.get("checked_date")
        if checked and checked > compiled:
            errors.append(f"{key}: checked_date after compiled_on")
        # Future target years belong in period/notes, not in event_date.
        for field in ("event_date", "published_date"):
            if checked and field in parsed_dates and parsed_dates[field] > checked:
                errors.append(f"{key}: {field} after checked_date")
    return errors


def search(sources, query="", doc_type=None, verification=None):
    terms = query.casefold().split()
    fields = ("title", "original_author", "publisher", "period", "tags", "notes")
    results = []
    for item in sources:
        if doc_type and item["doc_type"] != doc_type:
            continue
        if verification and item["verification"] != verification:
            continue
        text = " ".join(" ".join(item[f]) if isinstance(item[f], list) else item[f] for f in fields).casefold()
        if all(term in text for term in terms):
            results.append(item)
    return results


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--catalog", type=Path, default=CATALOG)
    commands = parser.add_subparsers(dest="command", required=True)
    lookup = commands.add_parser("search", help="Search metadata, not document full text")
    lookup.add_argument("query", nargs="?", default="")
    lookup.add_argument("--type", choices=sorted(TYPES))
    lookup.add_argument("--verification", choices=sorted(STATES))
    commands.add_parser("validate", help="Check metadata structure; does not check live URLs")
    commands.add_parser("stats")
    args = parser.parse_args()
    try:
        catalog = json.loads(args.catalog.read_text(encoding="utf-8-sig"))
        errors = validate(catalog)
    except (OSError, ValueError) as exc:
        emit({"ok": False, "error": str(exc)})
        return 1
    if errors:
        emit({"ok": False, "errors": errors})
        return 1
    sources = catalog["sources"]
    if args.command == "validate":
        emit({"ok": True, "records": len(sources), "live_urls_checked": False})
    elif args.command == "stats":
        emit({"compiled_on": catalog["compiled_on"], "records": len(sources),
              "types": dict(Counter(s["doc_type"] for s in sources)),
              "verification": dict(Counter(s["verification"] for s in sources)),
              "scope": catalog["scope"]})
    else:
        matches = search(sources, args.query, args.type, args.verification)
        emit({"count": len(matches), "metadata_only": True, "sources": matches,
              "note": "No match means absent from this seed catalog, not absent from public records."})
    return 0


if __name__ == "__main__":
    sys.exit(main())
