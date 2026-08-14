---
name: work-orders-org
description: "Single-work-order routed through the org. Like /work-orders but instead of a Sonnet agent doing the whole thing, the WO walks James -> Tim -> dept head -> junior with full review gates. Use for one targeted item that benefits from named accountability + cross-dept coordination. Invoke with /work-orders-org <ID> or /work-orders-org pick to be prompted."
---

# work-orders-org Skill

A single work-order pass through the org. No marathon, no cron — just one WO, end to end, with the chain of command and the comms bus engaged.

## When to use

- A single WO needs to ship cleanly, with John's review and dept-head pre-review.
- A WO crosses departments and you want explicit coordination on `dept-heads`.
- A WO is security/compliance-sensitive and you want named accountability.
- You want to trial-run the org on one item before kicking off `/marathon-org`.

For batches of 3+, prefer `/marathon-org`. For a one-line trivial fix, just edit it.

## Invocation

```
/work-orders-org BUG-141        Route a specific WO through the org
/work-orders-org pick           Read the backlog, propose top 1, ask user to confirm
/work-orders-org dry-run BUG-141  Show what would happen, don't spawn anyone
```

## Prerequisite

agent-org must be installed (see `agent-org/INSTALL.md`).

## Workflow

1. **Read the WO** from the backlog (id provided OR top-priority if `pick`).
2. **Smoke-check the comms db** is reachable: `python .claude/comms/comms.py stats`. If not, run `python .claude/comms/comms.py init`.
3. **Spawn `cto-james`** with the WO context. James's prompt:

   ```
   Single work order from the CEO:

   ID: {WO.id}
   Title: {WO.title}
   Priority: {WO.priority}
   Details: {WO.details}
   Context: {WO.context}
   Acceptance: {WO.acceptance}

   Brief Tim and John on c-suite. Stay engaged until the org reports back
   to you with a "ready to merge" summary, then post a final summary on
   c-suite addressed to ceo with the resolution and a confidence 1-5.
   ```

4. **Wait for James to report back** (his Agent call returns when he's done).
5. **Read the c-suite summary** addressed to `ceo`:
   ```bash
   python .claude/comms/comms.py read c-suite tim --limit 5 -v
   ```
   (Tim is on c-suite and can read it for the review.)
6. **Run the verification commands** for the project (pytest, ruff, npm test, etc.).
7. **Show the user**:
   - the comms summary (one line: "James says: BUG-141 fixed, conf 4")
   - the diff: `git diff main...HEAD`
   - John's review (post by John on c-suite, near the bottom)
   - test results
8. **Ask the user** to merge / reject / send back. On merge: commit + close the WO in the backlog. On send-back: post a follow-up directive on `c-suite` from the user (you can do this on their behalf by spawning James again with the new direction).

## Output

- The diff (committed if user merged)
- A close entry in `<backlog>/completed.md` if merged, or a status update in the source category file if iterating
- The comms log persisted in `.claude/comms.db` (audit trail)

## Why this isn't just `/work-orders`

`/work-orders` spawns Sonnet agents directly to ship items. Fast, cheap. But:
- No pre-review gate before the agent's work hits you.
- No cross-department awareness.
- No named accountability — every Sonnet agent is anonymous.

`/work-orders-org` adds the org's review chain and accountability at the cost of more tokens. Use it when the WO is worth the extra rigor.
