#!/usr/bin/env python3
"""Fetch, validate, and publish an upstream userscript snapshot."""
from __future__ import annotations
import hashlib, json, re, sys, urllib.request
from datetime import datetime, timezone
from pathlib import Path

UPSTREAM_URL = "https://gist.githubusercontent.com/JeiHyun/8ec8b56c4f0006ee3aa0ea002a05a269/raw/LL%20Gigascript.user.js"
ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
OUTPUT = DIST / "LL-Gigascript.user.js"
STATE = ROOT / "upstream-state.json"
MAX_BYTES = 5_000_000

def fetch():
    req = urllib.request.Request(UPSTREAM_URL, headers={"User-Agent": "CE-Gigascript-GitHub-Updater/1.0"})
    with urllib.request.urlopen(req, timeout=60) as response:
        if response.status != 200:
            raise RuntimeError(f"Upstream returned HTTP {response.status}")
        raw = response.read(MAX_BYTES + 1)
    if not raw or len(raw) > MAX_BYTES:
        raise RuntimeError("Empty upstream response or response exceeds size limit")
    try:
        return raw.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise RuntimeError("Upstream is not valid UTF-8") from exc

def validate(source):
    if "// ==UserScript==" not in source or "// ==/UserScript==" not in source:
        raise RuntimeError("Userscript metadata block missing")
    if not re.search(r"(?m)^\s*//\s*@name\s+\S", source):
        raise RuntimeError("Userscript @name missing")
    if not re.search(r"(?m)^\s*//\s*@version\s+\S", source):
        raise RuntimeError("Userscript @version missing")
    if "<html" in source[:500].lower() or "404: not found" in source[:500].lower():
        raise RuntimeError("Upstream response looks like an error page")
    return source

def apply_authorized_customizations(source):
    # Add only authorized customizations here. This template intentionally keeps
    # the upstream cartel-ID restriction unchanged.
    return source

def main():
    source = validate(fetch())
    generated = validate(apply_authorized_customizations(source))
    version = re.search(r"(?m)^\s*//\s*@version\s+([^\s]+)", generated)
    digest = hashlib.sha256(source.encode("utf-8")).hexdigest()
    if STATE.exists():
        try:
            previous = json.loads(STATE.read_text(encoding="utf-8"))
        except Exception:
            previous = {}
        if previous.get("upstream_sha256") == digest and OUTPUT.exists():
            print("Upstream unchanged; keeping the existing generated copy.")
            return
    DIST.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(generated, encoding="utf-8")
    STATE.write_text(json.dumps({
        "upstream_url": UPSTREAM_URL,
        "upstream_version": version.group(1) if version else "unknown",
        "upstream_sha256": digest,
        "checked_at_utc": datetime.now(timezone.utc).isoformat(),
        "generated_file": "dist/LL-Gigascript.user.js",
        "customization_policy": "authorized customizations only; cartel-ID restriction retained"
    }, indent=2) + "\n", encoding="utf-8")
    print(f"Validated upstream version {version.group(1) if version else 'unknown'}; SHA-256 {digest}")

if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)
