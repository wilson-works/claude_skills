#!/usr/bin/env python3
"""agent-org PreToolUse leak guard.

Blocks Write / Edit / MultiEdit / NotebookEdit calls whose content contains
credential material, and (optionally) blocks proprietary-marked content from
flowing into public paths.

Register in .claude/settings.json:

    "PreToolUse": [
      { "matcher": "Write|Edit|MultiEdit|NotebookEdit",
        "hooks": [ { "type": "command", "command": "python .claude/hooks/leak_guard.py" } ] }
    ]

What it blocks:
  1. SECRETS, anywhere: AWS access keys, GitHub / Slack / Anthropic tokens,
     Stripe live secret keys, Google API keys, PEM private-key blocks.
  2. MARKER RULES (optional, config-driven): content carrying a proprietary
     marker (e.g. "do not redistribute") being written under a public path
     prefix (e.g. a published docs tree, a public mirror checkout).

Config (optional): .claude/leak-guard.json
    {
      "extra_secret_patterns": ["\\bACME_INTERNAL_[A-Z0-9]{20}\\b"],
      "marker_rules": [
        { "markers": ["do not redistribute", "private fork", "internal use only"],
          "blocked_path_prefixes": ["public/", "dist-public/"] }
      ]
    }

Fail posture: FAIL-SAFE. Malformed hook input with content present -> DENY.
This is a safety hook, not a hygiene hook. Set LEAK_GUARD_DISABLE=1 to
short-circuit (debugging only).

Exit codes:
  0  allow
  2  block (Claude Code surfaces stderr to the model)

Self-test:  python leak_guard.py --selftest
"""

from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path

SECRET_PATTERNS: list[tuple[str, str]] = [
    ("AWS access key",        r"\bAKIA[0-9A-Z]{16}\b"),
    ("GitHub token",          r"\bgh[pousr]_[A-Za-z0-9]{36,}\b"),
    ("Slack token",           r"\bxox[baprs]-[A-Za-z0-9-]{10,}\b"),
    ("Anthropic API key",     r"\bsk-ant-[A-Za-z0-9_-]{20,}\b"),
    ("Stripe live secret",    r"\b[sr]k_live_[A-Za-z0-9]{16,}\b"),
    ("Stripe webhook secret", r"\bwhsec_[A-Za-z0-9]{24,}\b"),
    ("Google API key",        r"\bAIza[0-9A-Za-z_-]{35}\b"),
    ("Private key block",     r"-----BEGIN (?:RSA |EC |OPENSSH |DSA |PGP )?PRIVATE KEY(?: BLOCK)?-----"),
]

CONTENT_KEYS = ("content", "new_string", "new_source", "body", "text")
PATH_KEYS = ("file_path", "path", "notebook_path")


def _find_config() -> dict:
    for base in (os.environ.get("LEAK_GUARD_CONFIG"), ".claude/leak-guard.json"):
        if not base:
            continue
        p = Path(base)
        if p.is_file():
            try:
                return json.loads(p.read_text(encoding="utf-8"))
            except Exception:
                print(f"leak_guard: config {p} unreadable; using built-ins only", file=sys.stderr)
    return {}


def _collect(tool_input: dict) -> tuple[list[str], list[str]]:
    """Return (content strings, target paths) from a tool_input dict."""
    contents: list[str] = []
    paths: list[str] = []

    def walk(node):
        if isinstance(node, dict):
            for k, v in node.items():
                if isinstance(v, str):
                    if k in CONTENT_KEYS:
                        contents.append(v)
                    elif k in PATH_KEYS:
                        paths.append(v)
                else:
                    walk(v)
        elif isinstance(node, list):
            for item in node:
                walk(item)

    walk(tool_input)
    return contents, paths


def scan(tool_input: dict, config: dict) -> str | None:
    """Return a human-readable block reason, or None to allow."""
    contents, paths = _collect(tool_input)
    if not contents:
        return None

    patterns = list(SECRET_PATTERNS)
    for extra in config.get("extra_secret_patterns", []):
        patterns.append(("custom pattern", extra))

    for label, pat in patterns:
        for text in contents:
            if re.search(pat, text):
                return (f"LEAK GUARD: write blocked — content matches a {label} "
                        f"signature. Secrets never go into written files. Move the "
                        f"value to an environment variable or secret store and "
                        f"reference it instead.")

    norm_paths = [p.replace("\\", "/") for p in paths]
    for rule in config.get("marker_rules", []):
        markers = [m.lower() for m in rule.get("markers", [])]
        prefixes = rule.get("blocked_path_prefixes", [])
        if not markers or not prefixes:
            continue
        hit = next((m for m in markers for t in contents if m in t.lower()), None)
        if hit and any(any(np.startswith(pref) or f"/{pref}" in np for pref in prefixes)
                       for np in norm_paths):
            return (f"LEAK GUARD: write blocked — content is marked proprietary "
                    f"(\"{hit}\") and the target path is on a public prefix "
                    f"({', '.join(prefixes)}). Strip the marked content before "
                    f"publishing, or write it to a non-public path.")
    return None


def main() -> int:
    if os.environ.get("LEAK_GUARD_DISABLE") == "1":
        return 0
    raw = sys.stdin.read()
    if not raw.strip():
        return 0  # manual invocation / misconfiguration — nothing to judge
    brace = raw.find("{")  # tolerate BOM/encoding junk before the JSON
    if brace == -1:
        print("LEAK GUARD: unparseable hook input — failing safe (DENY). "
              "Set LEAK_GUARD_DISABLE=1 to bypass while debugging.", file=sys.stderr)
        return 2
    raw = raw[brace:]
    try:
        payload = json.loads(raw)
        tool_input = payload.get("tool_input") or {}
    except Exception:
        print("LEAK GUARD: unparseable hook input — failing safe (DENY). "
              "Set LEAK_GUARD_DISABLE=1 to bypass while debugging.", file=sys.stderr)
        return 2
    reason = scan(tool_input, _find_config())
    if reason:
        print(reason, file=sys.stderr)
        return 2
    return 0


def selftest() -> int:
    cases = [
        ("clean write", {"file_path": "src/a.py", "content": "print('hello')"}, None, True),
        ("aws key", {"file_path": "src/a.py", "content": "key=AKIAABCDEFGHIJKLMNOP"}, None, False),
        ("github token", {"file_path": "n.md", "content": "ghp_" + "a" * 36}, None, False),
        ("slack token", {"file_path": "n.md", "content": "xoxb-123456789012-abcdef"}, None, False),
        ("anthropic key", {"file_path": "n.md", "content": "sk-ant-" + "a" * 24}, None, False),
        ("stripe live", {"file_path": "n.md", "content": "sk_live_" + "a" * 24}, None, False),
        ("stripe test ok", {"file_path": "n.md", "content": "sk_test_" + "a" * 24}, None, True),
        ("pem block", {"file_path": "n.md", "content": "-----BEGIN PRIVATE KEY-----"}, None, False),
        ("edit new_string", {"file_path": "a.py", "old_string": "x", "new_string": "AKIAABCDEFGHIJKLMNOP"}, None, False),
        ("multiedit nested", {"file_path": "a.py", "edits": [{"old_string": "x", "new_string": "ghp_" + "b" * 36}]}, None, False),
        ("secret in old_string ok", {"file_path": "a.py", "old_string": "AKIAABCDEFGHIJKLMNOP", "new_string": "os.environ['AWS_KEY']"}, None, True),
        ("marker to public path", {"file_path": "public/guide.md", "content": "Do Not Redistribute. steps..."},
         {"marker_rules": [{"markers": ["do not redistribute"], "blocked_path_prefixes": ["public/"]}]}, False),
        ("marker to private path", {"file_path": "internal/guide.md", "content": "do not redistribute"},
         {"marker_rules": [{"markers": ["do not redistribute"], "blocked_path_prefixes": ["public/"]}]}, True),
        ("google api key", {"file_path": "n.md", "content": "AIza" + "a" * 35}, None, False),
    ]
    failed = 0
    for desc, tool_input, config, want_allow in cases:
        got_allow = scan(tool_input, config or {}) is None
        ok = got_allow == want_allow
        failed += 0 if ok else 1
        print(f"{'PASS' if ok else 'FAIL'}  {desc}  (allow={got_allow}, want={want_allow})")
    print(f"\n{len(cases) - failed}/{len(cases)} passed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(selftest() if "--selftest" in sys.argv else main())
