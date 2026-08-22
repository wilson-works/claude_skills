---
name: handoff
description: Compact the current conversation into a handoff document for another agent to pick up. Invoke with /handoff.
argument-hint: "What will the next session be used for? (or --wave N)"
---

Write a handoff document summarising the current conversation so a fresh agent can continue the work. Save it to a path produced by `mktemp -t handoff-XXXXXX.md` (read the file before you write to it).

Suggest the skills to be used, if any, by the next session.

Do not duplicate content already captured in other artifacts (PRDs, plans, ADRs, issues, commits, diffs). Reference them by path or URL instead.

If the user passed arguments, treat them as a description of what the next session will focus on and tailor the doc accordingly.

## `--wave N`

Writes the wave handoff for a wave-shaped run — a long session that works one wave per iteration, hands off to disk, and wakes with fresh context — instead of a temp file.

- Path: `<run-dir>/handoffs/wave-N.md`, unpadded `N`, in the run directory this session is working in.
- Exactly five headings, verbatim and in this order: `## Done`, `## Not done + why`, `## Next wave should`, `## How to verify`, `## Files touched`.
- `## How to verify` takes executable checks only — a command, or a file assertion, each with its expected result. Anything a reader must judge goes under `## Not done + why`.
- Reference-don't-duplicate still applies: the ledger, the diffs and the artifacts are already on disk.
- Keep the five headings stable across a run. A later wave reads them positionally, and a renamed heading reads as a missing section.
