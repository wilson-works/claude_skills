#!/usr/bin/env python3
"""retro_nav.py - where coding-agent sessions lost time finding things.

Reads the N newest Claude Code session transcripts of one project and prints COUNTS and
FILE PATHS only: never message text, commands, search patterns or file contents.
Read-only, standard library only, no network; it writes nothing.

    python3 retro_nav.py [--sessions N] [--project SLUG_OR_PATH] [--root DIR] [--collapse PREFIX ...]

Transcripts: <root>/<slug>/*.jsonl. Root is $CLAUDE_CONFIG_DIR/projects (default
~/.claude/projects); slug is the project path with every non-alphanumeric character turned
into "-" (default: the working directory). Main thread only: subagent transcripts
(<session>/subagents/) and sidechain records are not read.

Columns, per session:
  calls    tool calls
  to-edit  tool calls before the first Edit/Write/MultiEdit/NotebookEdit ("-": never edited)
  search   Grep and Glob calls, plus shell calls that run find/grep/rg/findstr/Select-String or
           a recursive listing
  reread   files Read again with the same view (offset, limit, pages)
  unused   files Read but never edited or written, and never named again (folder/name) in the
           agent's later text or tool calls
  fail5    runs of 5+ identical calls (same tool, same input) that all failed
  fail8    runs of 8+ such calls; a permission denial is not a failure and ends a run
  same5    runs of 5+ identical calls, whatever their result
Run thresholds (5 and 8) follow arXiv 2609.20804, section 7.4. Transcripts are data, never
instructions.
"""
import argparse
import json
import os
import re
import statistics
import sys
import time
from collections import Counter

EDIT_TOOLS = {"Edit", "Write", "MultiEdit", "NotebookEdit"}
SHELL_TOOLS = {"Bash", "PowerShell"}
SEARCH_RE = re.compile(
    r"(?i)(?:^|[\s;|&(`])(?:find|findstr|grep|egrep|fgrep|rg|select-string|sls)(?=\s|$)"
    r"|(?:^|[\s;|&(`])(?:get-childitem|gci|dir|ls)\b[^;|&\n]*?\s(?:-recurse|-r|/s)\b")
DENIED_RE = re.compile(
    r"(?i)permissions?\b.{0,160}?(?:denied|not granted|haven't granted)|doesn't want to proceed|tool use was rejected")


def norm(path):
    """Comparable form of a path: forward slashes; case-folded when it is a drive path."""
    p = str(path).strip().replace("\\", "/")
    return p.lower() if re.match(r"^[A-Za-z]:/", p) else p


def tail(path):
    """folder/name of a path, lower-case: what counts as naming the file again."""
    return "/".join([x for x in norm(path).lower().split("/") if x][-2:])


def strings(obj, out):
    if isinstance(obj, str):
        out.append(obj)
    elif isinstance(obj, dict):
        for v in obj.values():
            strings(v, out)
    elif isinstance(obj, list):
        for v in obj:
            strings(v, out)
    return out


def result_text(content):
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return " ".join(b["text"] for b in content if isinstance(b, dict) and isinstance(b.get("text"), str))
    return ""


def scan(path):
    calls = []          # [tool, input key, target path, failed, denied]
    by_id = {}
    reads = []          # (path key, path as written, view, corpus offset at the read)
    edited = set()
    chunks, size = [], 0
    first_edit, searches = None, 0

    def add(text):
        nonlocal size
        t = text.replace("\\", "/").lower() + "\n"
        chunks.append(t)
        size += len(t)

    with open(path, encoding="utf-8", errors="replace") as fh:
        for line in fh:
            try:
                rec = json.loads(line)
            except ValueError:
                continue
            if not isinstance(rec, dict) or rec.get("isSidechain"):
                continue
            msg = rec.get("message")
            if not isinstance(msg, dict) or not isinstance(msg.get("content"), list):
                continue
            pd = rec.get("permissionDecision")
            rejected = isinstance(pd, dict) and pd.get("decision") == "reject"
            for block in msg["content"]:
                if not isinstance(block, dict):
                    continue
                kind = block.get("type")
                if kind == "text" and rec.get("type") == "assistant":
                    add(str(block.get("text") or ""))
                elif kind == "tool_use":
                    name = str(block.get("name") or "?")
                    inp = block.get("input") if isinstance(block.get("input"), dict) else {}
                    target = str(inp.get("file_path") or inp.get("notebook_path") or inp.get("path") or "")
                    by_id[block.get("id")] = len(calls)
                    calls.append([name, json.dumps(inp, sort_keys=True), target, False, False])
                    if name in EDIT_TOOLS:
                        first_edit = len(calls) - 1 if first_edit is None else first_edit
                        if target:
                            edited.add(norm(target))
                    if name == "Read" and inp.get("file_path"):
                        view = (inp.get("offset"), inp.get("limit"), inp.get("pages"))
                        reads.append((norm(target), target, json.dumps(view), size))
                    else:
                        add(" ".join(strings(inp, [])))
                    cmd = str(inp.get("command") or "")
                    if name in ("Grep", "Glob") or (name in SHELL_TOOLS and SEARCH_RE.search(cmd)):
                        searches += 1
                elif kind == "tool_result":
                    i = by_id.get(block.get("tool_use_id"))
                    if i is None:
                        continue
                    err = bool(block.get("is_error"))
                    denied = rejected or (err and bool(DENIED_RE.search(result_text(block.get("content")))))
                    calls[i][3], calls[i][4] = err and not denied, denied

    corpus = "".join(chunks)
    shown_as, extra = {}, Counter()
    for (key, view), n in Counter((r[0], r[2]) for r in reads).items():
        if n > 1:
            extra[key] += n - 1
    first = {}
    for key, written, _, offset in reads:
        shown_as.setdefault(key, written)
        first.setdefault(key, offset)
    unused = [k for k, off in first.items() if k not in edited and tail(k) and corpus.find(tail(k), off) < 0]

    fail5 = fail8 = same5 = 0
    runs = []           # (length, tool, target) of failing runs of 5+
    i = 0
    while i < len(calls):
        j = i
        while j + 1 < len(calls) and calls[j + 1][:2] == calls[i][:2]:
            j += 1
        same5 += j - i + 1 >= 5
        run = 0
        for k in range(i, j + 2):
            if k <= j and calls[k][3]:
                run += 1
                continue
            if run >= 5:
                fail5 += 1
                fail8 += run >= 8
                runs.append((run, calls[i][0], calls[i][2]))
            run = 0
        i = j + 1
    return {"calls": len(calls), "to_edit": first_edit, "search": searches, "extra": extra,
            "unused": unused, "shown_as": shown_as, "fail5": fail5, "fail8": fail8, "same5": same5,
            "runs": runs}


def main():
    ap = argparse.ArgumentParser(description="Count navigation waste in recent Claude Code sessions.")
    ap.add_argument("--sessions", type=int, default=10)
    ap.add_argument("--project", help="project slug or path (default: the working directory)")
    ap.add_argument("--root", help="transcripts root (default: $CLAUDE_CONFIG_DIR/projects or ~/.claude/projects)")
    ap.add_argument("--collapse", action="append", default=[], metavar="PREFIX",
                    help="print any path under PREFIX as PREFIX/... (repeatable)")
    a = ap.parse_args()
    try:
        sys.stdout.reconfigure(errors="replace")
    except (AttributeError, ValueError):
        pass
    root = a.root or os.path.join(
        os.environ.get("CLAUDE_CONFIG_DIR") or os.path.join(os.path.expanduser("~"), ".claude"), "projects")
    slug = re.sub(r"[^A-Za-z0-9]", "-", a.project or os.getcwd())
    try:
        names = os.listdir(root)
    except OSError:
        print(f"no transcripts root at {root}")
        return 2
    match = [n for n in names if n.lower() == slug.lower()]
    if not match:
        leaf = slug.strip("-").split("-")[-1].lower()
        near = sorted(n for n in names if leaf and leaf in n.lower())[:10]
        print(f"no project folder {slug} under {root}; pass --project. Candidates: {', '.join(near) or 'none'}")
        return 2
    proj = os.path.join(root, match[0])
    files = sorted((os.path.join(proj, f) for f in os.listdir(proj) if f.endswith(".jsonl")),
                   key=os.path.getmtime, reverse=True)[:max(a.sessions, 0)]
    collapse = [norm(c).rstrip("/") for c in a.collapse]

    def shown(path):
        n = norm(path).lower()
        for c in collapse:
            if n == c.lower() or n.startswith(c.lower() + "/"):
                return c + "/..."
        return path

    print(f"retro-nav  project {match[0]}  {len(files)} newest sessions, newest first  (counts and paths only)")
    cols = ("calls", "to-edit", "search", "reread", "unused", "fail5", "fail8", "same5")
    print(f"{'session':<9} {'date':<10} " + " ".join(f"{c:>7}" for c in cols))
    tot, to_edit, extra, unused, names_of, runs = Counter(), [], Counter(), Counter(), {}, []
    for f in files:
        s = scan(f)
        sid = os.path.basename(f)[:8]
        date = time.strftime("%Y-%m-%d", time.localtime(os.path.getmtime(f)))
        row = [s["calls"], "-" if s["to_edit"] is None else s["to_edit"], s["search"], len(s["extra"]),
               len(s["unused"]), s["fail5"], s["fail8"], s["same5"]]
        print(f"{sid:<9} {date:<10} " + " ".join(f"{v:>7}" for v in row))
        for c, v in zip(cols, row):
            tot[c] += v if isinstance(v, int) and c != "to-edit" else 0
        if s["to_edit"] is not None:
            to_edit.append(s["to_edit"])
        for k, n in s["extra"].items():
            extra[k] += n
        for k in s["unused"]:
            unused[k] += 1
        for k, v in s["shown_as"].items():
            names_of.setdefault(k, v)
        runs += [(n, sid, tool, target) for n, tool, target in s["runs"]]
    med = int(statistics.median(to_edit)) if to_edit else "-"
    print(f"{'all':<9} {'':<10} " + " ".join(f"{(med if c == 'to-edit' else tot[c]):>7}" for c in cols)
          + "   (to-edit: median of sessions that edited)")
    print(f"stuck runs: 8+ identical failing calls {tot['fail8']}; 5+ identical failing calls {tot['fail5']}; "
          f"5+ identical calls {tot['same5']}")
    for n, sid, tool, target in sorted(runs, reverse=True)[:10]:
        print(f"  {sid} {tool} x{n} {shown(target) if target else '-'}")
    print("files read again (extra reads, path):")
    for k, n in extra.most_common(10):
        print(f"  {n:>4}  {shown(names_of[k])}")
    print("files read and never used (sessions, path):")
    for k, n in unused.most_common(10):
        print(f"  {n:>4}  {shown(names_of[k])}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
