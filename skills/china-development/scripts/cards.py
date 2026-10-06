#!/usr/bin/env python3
"""Retrieve complete decision cards and validate their source references."""
import argparse
from collections import Counter
from datetime import date
import json
from pathlib import Path
import re
import sys

import sources

ROOT = Path(__file__).resolve().parents[1]
CARDS = ROOT / "references" / "decision-cards.json"
LEVELS = {"national", "local_industry", "household_personal"}
LABELS = {"national": "国家发展", "local_industry": "地方与产业", "household_personal": "家庭与个人"}
KINDS = {"official_position", "rule", "descriptive_data", "causal_evidence", "analytical_method"}
KIND_LABELS = {"official_position": "官方论述", "rule": "规则文本", "descriptive_data": "描述性数据", "causal_evidence": "因果证据", "analytical_method": "方法来源"}
LIST_FIELDS = ("keywords", "required_context", "actions", "costs", "expected_benefits",
               "tradeoffs", "stop_conditions", "local_verification")
TEXT_FIELDS = ("id", "title", "level", "applies_to", "review_trigger", "limits", "checked_date")


def validate(cards, source_catalog):
    errors = sources.validate(source_catalog)
    if errors:
        return ["Source catalog: " + e for e in errors]
    if not isinstance(cards, dict) or cards.get("schema_version") != 1:
        return ["Unsupported decision card schema"]
    entries = cards.get("cards")
    if not isinstance(entries, list) or not entries:
        return ["cards must be a nonempty array"]
    source_map = {s["id"]: s for s in source_catalog["sources"]}
    seen = set()
    for index, card in enumerate(entries):
        prefix = f"cards[{index}]"
        if not isinstance(card, dict):
            errors.append(prefix + ": must be an object")
            continue
        for field in TEXT_FIELDS:
            if not isinstance(card.get(field), str) or not card[field].strip():
                errors.append(f"{prefix}: missing or invalid {field}")
        card_id = card.get("id")
        if not isinstance(card_id, str) or not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", card_id):
            errors.append(prefix + ": invalid id")
        elif card_id in seen:
            errors.append(prefix + ": duplicate id")
        else:
            seen.add(card_id)
        if not isinstance(card.get("level"), str) or card["level"] not in LEVELS:
            errors.append(prefix + ": invalid level")
        for field in LIST_FIELDS:
            value = card.get(field)
            if not isinstance(value, list) or not value or not all(isinstance(v, str) and v.strip() for v in value):
                errors.append(f"{prefix}: {field} must contain nonempty strings")
        try:
            checked = date.fromisoformat(card.get("checked_date"))
            if checked > date.fromisoformat(source_catalog["compiled_on"]):
                errors.append(prefix + ": card checked after catalog compilation")
        except (TypeError, ValueError):
            errors.append(prefix + ": invalid checked_date")
        evidence = card.get("evidence")
        if not isinstance(evidence, list) or not evidence:
            errors.append(prefix + ": evidence required")
            continue
        for e in evidence:
            if not isinstance(e, dict):
                errors.append(prefix + ": invalid evidence object")
                continue
            source_id = e.get("source_id")
            if not isinstance(source_id, str) or source_id not in source_map:
                errors.append(prefix + ": unresolved evidence source")
            elif source_map[source_id]["verification"] != "opened_fulltext":
                errors.append(prefix + ": evidence must refer to an opened text, not a portal or blocked page")
            if not isinstance(e.get("type"), str) or e["type"] not in KINDS:
                errors.append(prefix + ": unknown evidence type")
            for field in ("locator", "supports"):
                if not isinstance(e.get(field), str) or not e[field].strip():
                    errors.append(f"{prefix}: evidence needs {field}")
    return errors


def search(cards, query="", level=None):
    terms = query.casefold().split()
    matches = []
    for card in cards:
        if level and card["level"] != level:
            continue
        haystack = json.dumps(card, ensure_ascii=False).casefold()
        if all(term in haystack for term in terms):
            matches.append(card)
    return matches


def render(cards, source_map):
    lines = ["# 中国发展与民生行动条目", "", "由 decision-cards.json 自动生成。条目是研究与决策起点，具体资格、金额、时限和规则仍须当次核验。预期收益不等于实测效果。", ""]
    headings = [("required_context", "先补哪些条件"), ("actions", "行动步骤"), ("costs", "成本"),
                ("expected_benefits", "预期作用"), ("tradeoffs", "取舍"),
                ("stop_conditions", "暂停或改判条件"), ("local_verification", "本地核验")]
    for card in cards:
        lines += [f"## {card['id']} · {card['title']}", "",
                  f"层级：{LABELS[card['level']]}；资料核验：{card['checked_date']}。", "",
                  card["applies_to"], ""]
        for field, label in headings:
            lines += [f"**{label}**", ""]
            lines += ["- " + value for value in card[field]]
            lines.append("")
        lines += ["**证据及其支持范围**", ""]
        for e in card["evidence"]:
            source = source_map[e["source_id"]]
            lines.append(f"- [{source['title']}]({source['url']})（{KIND_LABELS[e['type']]}；{e['locator']}）：{e['supports']}")
        lines += ["", "**复查信号**：" + card["review_trigger"], "", "**边界**：" + card["limits"], ""]
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    lookup = commands.add_parser("search", help="Return whole cards; does not rank desirability")
    lookup.add_argument("query", nargs="?", default="")
    lookup.add_argument("--level", choices=sorted(LEVELS))
    lookup = commands.add_parser("show")
    lookup.add_argument("id")
    commands.add_parser("validate")
    commands.add_parser("stats")
    commands.add_parser("render", help="Print a human-readable Markdown edition")
    args = parser.parse_args()
    try:
        catalog = json.loads(sources.CATALOG.read_text(encoding="utf-8-sig"))
        card_catalog = json.loads(CARDS.read_text(encoding="utf-8-sig"))
        errors = validate(card_catalog, catalog)
    except (OSError, ValueError) as exc:
        sources.emit({"ok": False, "error": str(exc)})
        return 1
    if errors:
        sources.emit({"ok": False, "errors": errors})
        return 1
    cards = card_catalog["cards"]
    source_map = {s["id"]: s for s in catalog["sources"]}
    if args.command == "validate":
        sources.emit({"ok": True, "cards": len(cards), "source_links_resolve": True,
                      "semantics_or_current_effectiveness_verified": False})
    elif args.command == "stats":
        sources.emit({"cards": len(cards), "levels": dict(Counter(c["level"] for c in cards)),
                      "evidence_types": dict(Counter(e["type"] for c in cards for e in c["evidence"]))})
    elif args.command == "render":
        sys.stdout.reconfigure(encoding="utf-8")
        print(render(cards, source_map))
    else:
        matches = search(cards, args.query, args.level) if args.command == "search" else [c for c in cards if c["id"] == args.id]
        relevant_ids = {e["source_id"] for c in matches for e in c["evidence"]}
        sources.emit({"count": len(matches), "cards": matches,
                      "sources": [s for s in catalog["sources"] if s["id"] in relevant_ids],
                      "ranked": False,
                      "note": "返回完整条目及来源元数据。零结果不代表问题无解；文件内顺序不是建议优先级。现行规则需当次核验。"})
        if args.command == "show" and not matches:
            return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
