---
name: marathon-org
description: "Org-routed walkaway marathon. Same loop as /marathon-orders, but every wave routes through cto-james -> tim -> dept head -> junior with the comms bus and path claims active. Use when you want unattended multi-WO execution with full review gates and named accountability instead of one-off Opus agents. Invoke with /marathon-org [category] [--wave N] [--stop] [--status]."
---

# marathon-org Skill

The org-aware sibling of `/marathon-orders`. Same state file, same cron cadence, same review gate. The only difference: every work order is delivered to the org through `cto-james`, not to a generic Opus dev agent.

## When to use this vs /marathon-orders

- **`/marathon-orders`** — fastest path: one Opus agent per work order. No org overhead. Right when the queue is shallow and the WOs are independent.
- **`/marathon-org`** — every WO walks through the full chain: James (priority + accountability) -> Tim (route to right dept) -> Cindy/Gavin/Diana/Rachel/Josh (assign to junior, pre-review) -> Marcus/Priya/etc. (implement) -> head pre-review -> Tim digest -> John code review. Right when you want named accountability, dept-aware routing, and pre-review gates that catch slop before John sees it.

For the same backlog, `/marathon-org` runs slower per WO but produces cleaner diffs and better cross-department coordination because everyone knows who's editing what via `comms claims`.

## Configure for your project

Same placeholders as `/marathon-orders`. This skill reuses that infrastructure:

- `<your-project-backlog-path>` — directory holding `bugs.md`, `design.md`, `features.md`, `tech-debt.md`, `completed.md`
- `<state-dir>` — usually `<project-root>/.claude`
- `<project-root>` — repo root

Plus the agent-org install must be complete (see `agent-org/INSTALL.md`):
- `.claude/agents/cto-james.md` and the rest of the 18 agents present
- `.claude/comms/comms.py` present
- `.claude/agents/org.config.json` configured for your repo
- Path-guard hook registered

## Invocation

```
/marathon-org                  Fresh start, all categories, wave size 1
/marathon-org bugs             Bugs only
/marathon-org features         Features only
/marathon-org tech-debt        Tech debt only
/marathon-org design           Design only
/marathon-org --wave 2         2 work orders concurrent
/marathon-org bugs --wave 2    Bugs only, 2 at a time
/marathon-org --stop           Pause after current wave
/marathon-org --status         Current wave + queue + claims + comms tail
/marathon-org --continue       Manual cron re-entry
/marathon-org dry-run          Show queue, don't launch
```

## State file

`<state-dir>/marathon-org-state.json`. Schema is identical to `marathon-orders` (see `/marathon-orders` SKILL.md), with one extra field per in-flight item:

```json
"orgTrace": {
  "ctoBriefedAt": "ISO",
  "tim_routed_to": "cindy",
  "department": "backend",
  "junior_assigned": "marcus",
  "claimsHeld": ["packages/tax-mapping/loader.py"]
}
```

This lets the wave-tick reconstruct who's holding what without re-reading the comms log.

## How a wave runs (the org-routed version)

### Phase 1 (fresh start) — same as marathon-orders
1. Prune `completed.md`, parse the backlog, sort by priority + age, present the run plan.
2. Pre-flight `settings.json` permission additions (same five paths as `/marathon-orders`, plus `Bash(python .claude/comms/comms.py:*)`).
3. Confirm with the user. Write state file. Register the cron.

### Phase 2 (wave launch) — org-routed
For each WO popped from `queue`:

1. **Brief James** via Agent tool with `subagent_type=cto-james`. Prompt template:

   ```
   New work order from the backlog:

   ID: {WO.id}
   Title: {WO.title}
   Priority: {WO.priority}
   Category: {WO.category}

   Details:
   {WO.details}

   Context:
   {WO.context}

   Acceptance:
   {WO.acceptance}

   Direction: drive this through the org. Brief Tim and John on c-suite.
   When the org reports back to you on c-suite that the work is reviewed
   and ready to merge, post a final summary on c-suite addressed to me
   (the CEO, channel: c-suite, --to ceo) with the resolution and a
   confidence 1-5.
   ```

   (`ceo` is reserved as the c-suite recipient label for posts intended for the human; comms.py treats it as a valid `--to` value but no agent has its name.)

2. **Trace into state**: record the cron tick that James was launched on, the WO id, and the marathon branch (`marathon-org/{WO.id}`).

3. **Tim spawns the dept head** via `subagent_type=head-{department}-{name}` (e.g., `head-backend-cindy`). Tim's prompt is:

   ```
   {WO summary}
   {John's brief}

   Take this through your team. Pre-review before passing back to me.
   ```

4. **Dept head spawns the junior** via `subagent_type=junior-{department}-{name}`. Junior claims, implements, reports back on `dev-floor`.

5. **Pre-review chain**: junior -> dept head -> Tim -> John. John's review IS the merge gate.

### Phase 3 (cron tick) — same gates as marathon-orders, but driven by John
- Read state. Check the comms log: are any in-flight WOs reporting back to `c-suite`?
- For each WO with a James-final-summary on c-suite:
  - Pull the diff for `marathon-org/{WO.id}`.
  - Run the project's verification commands (`pytest`, `ruff`, `npm test`, etc.).
  - Read John's review (already on c-suite from his pre-merge sign-off).
  - If confidence >= 3 AND tests green AND John approved: merge to main, move WO to `completed`, release any open comms claims for that WO.
  - If confidence 1-2 OR tests red: ask the user (review gate). On reject: move to `failed` with reason.

### Phase 4 (cleanup)
When `queue` is empty AND no in-flight: post a final c-suite message from James (via a final Agent call) summarizing the run. Delete the cron. Mark `status: complete`.

## Differences vs /marathon-orders worth knowing

| Aspect | marathon-orders | marathon-org |
|--------|-----------------|--------------|
| Agent count per WO | 1 (Opus dev) | 4 minimum (James, Tim, head, junior) + John for review |
| Token cost per WO | ~1x | ~2-2.5x |
| Cross-WO coordination | none | claims + dev-floor visibility |
| Pre-review gate | none (relies on cron review) | dept head pre-reviews before John |
| Audit trail | state file only | state file + full comms log |
| Best for | shallow queue, independent WOs | deep queue, dept overlap, security-sensitive items |

## Inspecting a running marathon-org

```bash
# overall status
/marathon-org --status

# read what James has heard recently
python .claude/comms/comms.py read c-suite james --limit 30

# read what's flowing on dept-heads
python .claude/comms/comms.py read dept-heads tim --limit 50

# see active claims (who's editing what right now)
python .claude/comms/comms.py claims --active

# trace a specific WO across all channels
python .claude/comms/comms.py read c-suite james --limit 100 | grep BUG-141
python .claude/comms/comms.py read dept-heads tim --limit 100 | grep BUG-141
python .claude/comms/comms.py read dev-floor cindy --limit 100 | grep BUG-141
```

## Hard rules during a marathon-org

- The cron tick NEVER spawns juniors directly. Only James does (via Tim, via the head). Skipping the chain breaks the audit trail.
- Claims are mandatory. The path_guard hook will block any unauthorized edit anyway.
- Review gates: confidence < 3 OR tests red = ask the human. No "best effort" merging in unattended mode.
- `--stop` pauses cleanly: it lets in-flight juniors finish their current edit, then halts the cron. It does NOT yank a junior mid-edit.
