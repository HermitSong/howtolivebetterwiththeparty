#!/usr/bin/env python3
"""Run the repository's offline checks using only the Python standard library."""
import json
from pathlib import Path
import re
import subprocess
import sys
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
SKILL = Path("skills/china-development")
IGNORED_DIRS = {".git", "__pycache__", ".venv", "node_modules"}
PRIVATE_PATTERNS = {
    "absolute Windows path": re.compile(r"\b[A-Za-z]:[\\/]"),
    "private Unix path": re.compile(r"(?<![\w:])/(?:Users|home|root|private|tmp|var/tmp)/"),
    "UNC path": re.compile(r"\\\\[A-Za-z0-9_.-]+\\[A-Za-z0-9_$.-]+"),
    "GitHub token": re.compile(r"\b(?:gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,})\b"),
    "API key": re.compile(r"\bsk-(?:proj-|svcacct-)?[A-Za-z0-9_-]{20,}\b"),
    "AWS access key": re.compile(r"\b(?:AKIA|ASIA)[A-Z0-9]{16}\b"),
    "Slack token": re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{20,}\b"),
    "Google API key": re.compile(r"\bAIza[A-Za-z0-9_-]{35}\b"),
    "private key": re.compile(r"-----BEGIN (?:[A-Z]+ )?PRIVATE KEY-----"),
}
INLINE_LINK = re.compile(
    r"\]\(\s*(<[^>\n]+>|(?:\\.|[^()\s\\]|\([^()\n]*\))+)"
    r"(?:\s+(?:\"[^\"\n]*\"|'[^'\n]*'|\([^\)\n]*\)))?\s*\)"
)
REFERENCE_LINK = re.compile(r"(?m)^[ \t]{0,3}\[[^\]\n]+\]:[ \t]*(<[^>\n]+>|\S+)")


def markdown_links(text):
    """Read inline/image destinations and reference definitions, excluding code."""
    visible = []
    fence = None
    for line in text.splitlines(keepends=True):
        marker = re.match(r"^[ \t]{0,3}(`{3,}|~{3,})", line)
        if fence:
            if marker and marker[1][0] == fence[0] and len(marker[1]) >= len(fence):
                fence = None
            visible.append("\n" if line.endswith("\n") else "")
        elif marker:
            fence = marker[1]
            visible.append("\n" if line.endswith("\n") else "")
        else:
            visible.append(re.sub(r"(`+)(.*?)\1", "", line))
    prose = "".join(visible)
    for pattern in (INLINE_LINK, REFERENCE_LINK):
        for match in pattern.finditer(prose):
            destination = match[1].removeprefix("<").removesuffix(">")
            destination = re.sub(r"\\([\\() #])", r"\1", destination)
            yield prose.count("\n", 0, match.start()) + 1, destination


def scan_files():
    errors = []
    counts = {"text_files_scanned": 0, "binary_files_not_scanned": 0,
              "markdown_files": 0, "local_link_targets_checked": 0,
              "http_links_not_fetched": 0}
    for path in sorted(ROOT.rglob("*")):
        relative = path.relative_to(ROOT)
        if any(part in IGNORED_DIRS for part in relative.parts) or not path.is_file():
            continue
        name = relative.as_posix()
        if not path.resolve().is_relative_to(ROOT):
            errors.append(f"{name}: file resolves outside the repository")
            continue
        try:
            data = path.read_bytes()
            if b"\0" in data:
                counts["binary_files_not_scanned"] += 1
                continue
            text = data.decode("utf-8-sig")
        except UnicodeDecodeError:
            counts["binary_files_not_scanned"] += 1
            continue
        except OSError:
            errors.append(f"{name}: could not read file")
            continue
        counts["text_files_scanned"] += 1
        for label, pattern in PRIVATE_PATTERNS.items():
            for match in pattern.finditer(text):
                line = text.count("\n", 0, match.start()) + 1
                # Never print the suspected credential or private path.
                errors.append(f"{name}:{line}: possible {label}")
        if path.suffix.lower() != ".md":
            continue
        counts["markdown_files"] += 1
        for line, destination in markdown_links(text):
            try:
                url = urlsplit(destination)
            except ValueError:
                errors.append(f"{name}:{line}: malformed link")
                continue
            if url.scheme or url.netloc:
                if url.scheme in {"http", "https"} or url.netloc:
                    counts["http_links_not_fetched"] += 1
                continue
            if not url.path:
                continue
            target_path = unquote(url.path)
            target = ((ROOT / target_path.lstrip("/")) if target_path.startswith("/")
                      else (path.parent / target_path)).resolve()
            counts["local_link_targets_checked"] += 1
            if not target.is_relative_to(ROOT):
                errors.append(f"{name}:{line}: link resolves outside the repository")
            elif not target.exists():
                errors.append(f"{name}:{line}: missing local link target {target.relative_to(ROOT).as_posix()}")
    return counts, errors


def run_script(script, *arguments, json_result=False):
    result = subprocess.run(
        [sys.executable, "-B", "-X", "utf8", script.as_posix(), *arguments],
        cwd=ROOT, capture_output=True, encoding="utf-8",
    )
    if result.returncode:
        detail = (result.stdout + result.stderr).strip().replace(str(ROOT), ".")
        raise ValueError(f"{script.as_posix()} failed:\n{detail}")
    if json_result:
        payload = json.loads(result.stdout)
        if payload.get("ok") is not True:
            raise ValueError(f"{script.as_posix()}: validation did not report success")
        return payload
    return None


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    counts, errors = scan_files()
    if errors:
        print(json.dumps({"ok": False, "errors": errors}, ensure_ascii=False, indent=2))
        return 1
    try:
        sources = run_script(SKILL / "scripts/sources.py", "validate", json_result=True)
        cards = run_script(SKILL / "scripts/cards.py", "validate", json_result=True)
        run_script(Path("tools/build_book.py"), "--check")
    except (OSError, ValueError) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False, indent=2))
        return 1
    print(json.dumps({
        "ok": True,
        "source_records": sources["records"],
        "decision_cards": cards["cards"],
        **counts,
        "source_and_card_validation": "passed",
        "local_link_targets": "exist within repository",
        "private_path_and_token_patterns": "no matches in scanned text",
        "generated_book_consistency": "passed",
        "limits": "Offline checks only; no live URL, policy validity, eligibility or outcome verification.",
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
