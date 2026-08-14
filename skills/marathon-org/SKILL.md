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

## Execution model (READ FIRST — overrides the literal chain below)

Current Claude Code (v2.1.172+) supports **nested sub-agents to depth 5**, so the literal relay chain (cto-james → Tim → head → junior → John) is mechanically possible. This skill still defaults to **flattened orchestration** deliberately: it is roughly half the token cost per WO (no relay retelling at each hop), every spawn is visible in one transcript, and it works identically on older versions where nested spawn is unavailable. Route literally only when you specifically want the relay hops in the comms audit trail and accept the cost.

Default mode: the **top-level orchestrator (this session) performs every spawn directly**. Read each "X spawns Y" step below as "the orchestrator spawns Y on behalf of X":

- Spawn the **department head** agent (write-capable) to implement the WO in-territory.
- Spawn **chief-engineer-john** (review-only) as the merge gate.
- Optionally spawn **cto-james** / **Tim** first for advisory direction — they return judgment, they do not spawn. The junior tier collapses into the head.

Preserve everything that matters — comms claims, path-guard territory, the verification gate, independent review — and drop only the spawn-chain theater. The org-routed marathon's value is the named accountability + review gates, which survive this flattening intact.

## Configure for your project

Same placeholders as `/marathon-orders`. This skill reuses that infrastructure:

- `<your-project-backlog-path>` — directory holding `bugs.md`, `design.md`, `features.md`, `tech-debt.md`, `completed.md`
- `<state-dir>` — usually `<project-root>/.claude`
- `<project-root>` — repo root

Plus the agent-org install must be complete (see `agent-org/INSTALL.md`):
- the CTO-branch agents present (`cto-james`, `exec-assistant-tim`, the dept heads, `chief-engineer-john`, and the juniors) — this is the chain `/marathon-org` drives, regardless of how many advisory branches your org also installs
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

3. **The orchestrator spawns the dept head** (on Tim's behalf — per the Execution model above; Tim cannot spawn) via `subagent_type=head-{department}-{name}` (e.g., `head-backend-cindy`). The prompt is:

   ```
   {WO summary}
   {John's brief}

   Take this through your team. Pre-review before passing back to me.
   ```

4. **The orchestrator spawns the junior** (on the head's behalf; or collapse the junior into the head and have the head implement directly) via `subagent_type=junior-{department}-{name}`. The implementer claims, implements, reports back on `dev-floor`.

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

### What James's final wave summary looks like on c-suite

Per the Phase 2 brief, James closes each WO with a c-suite post addressed to `ceo` carrying the resolution and a confidence 1-5 — this is the post the Phase 3 cron tick parses. Synthetic example:

```
python .claude/comms/comms.py post c-suite james --to ceo --wo BUG-141 \
  --subject "BUG-141 reviewed & ready to merge" \
  "BUG-141 resolved. Root cause: tax-mapping loader dropped rows w/ null county code.
Fix: default-to-state fallback in packages/tax-mapping/loader.py + regression test.
Route: tim -> cindy (backend) -> marcus. Cindy pre-review: pass. John: approved, no findings.
pytest green | ruff clean. Branch marathon-org/BUG-141. Confidence: 4/5."
```

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

## Failure Modes

1. **John rejects the same WO twice**: do not launch a third implement→review round — a rejection loop burns tokens without producing new information. Park the WO as `blocked` in the state file with John's last review verbatim as the reason, release its claims, and advance to the next WO. Blocked WOs surface in `--status` and the final James summary for the human to re-scope.
2. **comms.py unreachable or DB locked**: the bus is the audit trail, not the engine. Fall back to direct orchestration — spawn head + John as normal, carry the routing trace in the state file's `orgTrace` only, and note "comms unavailable" in that wave's report. Do not retry-loop the bus mid-wave; re-test it on the next cron tick.
3. **Stale path claim blocking a lane**: `comms.py claims --active` to find the holder. If the holder's WO is no longer in-flight per the state file (completed, failed, or parked), clear it: `python .claude/comms/comms.py release --path <path> <holder>`. Never release a claim whose WO is still in-flight — that is a real conflict; sequence the WOs instead.
4. **A spawned head never reports back**: an implementer silent past one full cron interval — no comms post, no new commits on `marathon-org/{WO.id}` — is timed out. Mark the wave `failed-timeout`, release its claims, and requeue the WO once for a fresh spawn on the next tick. A second timeout parks it as `blocked` (see #1).

## Hard rules during a marathon-org

- Every WO's spawn set is the same: implementer (dept head, write-capable) + John (review gate), with James/Tim advisory when direction is ambiguous. The cron tick never skips the head or the John review to "save a spawn" — the pre-review chain IS the product. (Per the Execution model above, the orchestrator does the spawning on the org's behalf; the accountability trail lives in the comms posts, not in who literally called the Agent tool.)
- Claims are mandatory. The path_guard hook will block any unauthorized edit anyway.
- Review gates: confidence < 3 OR tests red = ask the human. No "best effort" merging in unattended mode.
- `--stop` pauses cleanly: it lets in-flight juniors finish their current edit, then halts the cron. It does NOT yank a junior mid-edit.
