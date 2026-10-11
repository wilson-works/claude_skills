#!/usr/bin/env python3
"""skill_lint.py - tier-2 lint for a folder of Claude Code skills. Standard library only; no network, no model.

Tier 1 is first-party: `claude plugin validate <skills-folder> --strict` parses every frontmatter and names
unknown fields. This script makes the checks tier 1 does not:

  PARSE      frontmatter missing, never closed, or a quoted value never closes   -> exit 1
  NAME       frontmatter name (after any "ns:" prefix) differs from the skill's folder; the validator passes it -> exit 1
  DUPLICATE  one skill name at more than one path (each name is then counted once)
  COLLIDE    two descriptions near-collide: TF-IDF cosine >= --threshold over description + when_to_use
  UNFILLED   <placeholders> a "Configure for your project" section asks you to replace, still in the file
  BUDGET     the skill listing's size against its budget at --context-tokens

Listing facts, https://code.claude.com/docs/en/skills#skill-descriptions-are-cut-short : the listing carries
every skill's name plus its description and when_to_use, cut at 1,536 characters; its character budget is 1%
of the context window; when it overflows, the least-used skills lose their descriptions first. A skill with
`disable-model-invocation: true` is left out of it. The docs give no characters-per-token figure; 4 is assumed.
BUDGET reads each frontmatter as written: a skill tier 1 says fails to parse is listed at runtime by name only,
with its flags dropped.

Usage:  skill_lint.py [SKILLS_DIR ...] [--context-tokens N] [--threshold X]
        SKILLS_DIR defaults to ~/.claude/skills. Each folder is linted on its own.
Output: a Markdown table, path | check | result, per folder. Exit 1 if any PARSE row, 2 if a folder is missing.
"""
import argparse
import math
import os
import re
import sys
from collections import Counter

ENTRY_CAP = 1536        # characters of description + when_to_use kept per listing entry
BUDGET_SHARE = 0.01     # share of the context window the listing gets
CHARS_PER_TOKEN = 4     # assumption, stated above
KEY = re.compile(r"^([A-Za-z0-9_-]+):(?:[ \t]+(.*))?$")
CONFIGURE = re.compile(r"^#{2,3}[ \t]+Configure for your project\b", re.I | re.M)
STOP = set("""about after also and any are args based before but can does each for from has have how into
its not one only that the their them then this use used uses using when where which while who will with
without you your invoke invoked""".split())


def close_at(buf, q):
    """Index of the quote that closes a value opened by q, or None."""
    k = 0
    while k < len(buf):
        if q == '"' and buf[k] == "\\":
            k += 2
            continue
        if buf[k] == q:
            if q == "'" and buf[k + 1:k + 2] == "'":
                k += 2
                continue
            return k
        k += 1
    return None


def read_frontmatter(text):
    """Return (top-level scalar fields, error). Lists and maps under a key are skipped, not read."""
    lines = text.splitlines()
    if not lines or lines[0].rstrip() != "---":
        return None, "no frontmatter: line 1 is not ---"
    end = next((i for i in range(1, len(lines)) if lines[i].rstrip() == "---"), None)
    if end is None:
        return None, "frontmatter never closed: no second --- line"
    fm, fields, i = lines[1:end], {}, 0
    while i < len(fm):
        m = KEY.match(fm[i])
        i += 1
        if not m:
            continue
        key, val = m.group(1), (m.group(2) or "").strip()
        if val[:1] in ('"', "'"):
            q, buf = val[0], val[1:]
            while close_at(buf, q) is None:
                if i >= len(fm):
                    return None, f"{key}: quoted value never closes"
                buf += " " + fm[i].strip()
                i += 1
            s = buf[:close_at(buf, q)]
            fields[key] = s.replace("''", "'") if q == "'" else re.sub(r"\\(.)", r"\1", s)
        else:
            block = val[:1] in ("|", ">")
            parts = [] if block else [re.sub(r"[ \t]+#.*$", "", val)]
            while i < len(fm) and (fm[i][:1] in (" ", "\t") or (block and not fm[i].strip())):
                parts.append(fm[i].strip())
                i += 1
            fields[key] = " ".join(p for p in parts if p)
    return fields, None


def stem(w):
    if w.endswith("ies") and len(w) > 5:
        return w[:-3] + "y"
    for suf in ("ing", "ed", "s"):
        if w.endswith(suf) and not w.endswith("ss") and len(w) - len(suf) >= 4:
            return w[:-len(suf)]
    return w


def vector(text):
    return Counter(stem(w) for w in re.findall(r"[a-z0-9]+", text.lower())
                   if len(w) > 2 and w not in STOP and not w.isdigit())


def unfilled(body):
    m = CONFIGURE.search(body)
    if not m:
        return []
    rest = body[m.end():]
    nxt = re.search(r"^#{1,3}[ \t]", rest, re.M)
    return sorted(set(re.findall(r"<([A-Za-z][\w.-]*)>", rest[:nxt.start()] if nxt else rest)))


def lint(root, context_tokens, threshold):
    skills, rows = [], []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = sorted(d for d in dirnames if not d.startswith("."))
        if "SKILL.md" not in filenames:
            continue
        path = os.path.join(dirpath, "SKILL.md")
        rel = os.path.relpath(path, root).replace(os.sep, "/")
        with open(path, encoding="utf-8-sig", errors="replace") as fh:
            text = fh.read()
        fields, err = read_frontmatter(text)
        if err:
            rows.append((rel, "PARSE", err))
            fields = {}
        if fields.get("name") and fields["name"].split(":")[-1] != os.path.basename(dirpath):  # "ns:folder" is fine
            rows.append((rel, "NAME", f"'{fields['name']}' in a folder named '{os.path.basename(dirpath)}'"))
        desc = " ".join(fields.get(k, "") for k in ("description", "when_to_use")).strip()
        skills.append({"rel": rel, "name": fields.get("name") or os.path.basename(dirpath), "text": desc,
                       "hidden": fields.get("disable-model-invocation", "").lower() == "true"})
        holes = unfilled(text)
        if holes:
            rows.append((rel, "UNFILLED", f"{len(holes)}: " + ", ".join(f"<{h}>" for h in holes)))

    by_name = {}
    for s in skills:
        by_name.setdefault(s["name"], []).append(s)
    reps = []
    for name, group in sorted(by_name.items()):
        group.sort(key=lambda s: (s["rel"].count("/"), s["rel"]))
        reps.append(group[0])
        if len(group) > 1:
            differ = "" if len({s["text"] for s in group}) == 1 else ", descriptions differ"
            rows.append((group[0]["rel"], "DUPLICATE",
                         f"{len(group)} copies of '{name}'{differ}; also " + ", ".join(s["rel"] for s in group[1:])))

    docs = [(s, vector(s["text"])) for s in reps if s["text"]]
    df = Counter(t for _, v in docs for t in v)
    idf = {t: math.log((1 + len(docs)) / (1 + n)) + 1 for t, n in df.items()}
    vecs = []
    for s, v in docs:
        w = {t: n * idf[t] for t, n in v.items()}
        norm = math.sqrt(sum(x * x for x in w.values())) or 1.0
        vecs.append((s, {t: x / norm for t, x in w.items()}))
    pairs = []
    for a in range(len(vecs)):
        for b in range(a + 1, len(vecs)):
            va, vb = vecs[a][1], vecs[b][1]
            if len(va) > len(vb):
                va, vb = vb, va
            cos = sum(x * vb.get(t, 0.0) for t, x in va.items())
            if cos >= threshold:
                pairs.append((cos, vecs[a][0], vecs[b][0]))
    for cos, s, t in sorted(pairs, key=lambda p: -p[0]):
        rows.append((s["rel"], "COLLIDE", f"{cos:.2f} with {t['rel']}"))

    listed = [s for s in reps if not s["hidden"]]
    total = sum(len(s["name"]) + min(len(s["text"]), ENTRY_CAP) for s in listed)
    budget = int(context_tokens * BUDGET_SHARE * CHARS_PER_TOKEN)
    rows.append((".", "BUDGET", f"{len(listed)} listed, {len(reps) - len(listed)} typed-only left out: {total} chars "
                 f"vs {budget} at {context_tokens} tokens ({'OVER' if total > budget else 'fits'}); fits from "
                 f"{math.ceil(total / (BUDGET_SHARE * CHARS_PER_TOKEN))} tokens"))
    cut = sum(1 for s in listed if len(s["text"]) > ENTRY_CAP)
    big = sorted(listed, key=lambda s: -len(s["text"]))[:5]
    rows.append((".", "BUDGET", f"{cut} descriptions over {ENTRY_CAP} chars; largest: "
                 + ", ".join(f"{s['name']} {len(s['text'])}" for s in big)))

    order = {"PARSE": 0, "NAME": 1, "DUPLICATE": 2, "COLLIDE": 3, "UNFILLED": 4, "BUDGET": 5}
    rows.sort(key=lambda r: order[r[1]])
    print(f"## skill_lint: {root} ({len(skills)} SKILL.md, {len(by_name)} names; COLLIDE at cosine >= {threshold})\n")
    print("| path | check | result |\n|---|---|---|")
    for r in rows:
        print("| " + " | ".join(c.replace("|", "\\|") for c in r) + " |")
    count = Counter(r[1] for r in rows)
    print("\nsummary: " + ", ".join(f"{k} {count.get(k, 0)}" for k in order if k != "BUDGET") + "\n")
    return count.get("PARSE", 0) + count.get("NAME", 0)


def main():
    ap = argparse.ArgumentParser(description="Tier-2 lint for a folder of Claude Code skills.")
    ap.add_argument("dirs", nargs="*", default=[os.path.join("~", ".claude", "skills")])
    ap.add_argument("--context-tokens", type=int, default=200000, help="context window size (default 200000)")
    ap.add_argument("--threshold", type=float, default=0.5, help="COLLIDE cosine threshold (default 0.5)")
    args = ap.parse_args()
    sys.stdout.reconfigure(errors="replace")
    parse_failures = 0
    for d in args.dirs:
        root = os.path.expanduser(d)
        if not os.path.isdir(root):
            print(f"skill_lint: no such folder: {root}", file=sys.stderr)
            return 2
        parse_failures += lint(root, args.context_tokens, args.threshold)
    return 1 if parse_failures else 0


if __name__ == "__main__":
    sys.exit(main())
