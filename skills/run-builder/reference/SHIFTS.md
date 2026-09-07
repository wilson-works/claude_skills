# Shifts — the four deltas, expanded

Source: design spec §6; owner requirement §A.3 of
`D:\Hub\50-AI\fleet-ops\notes\2026-08-31-run-standard-research.md`. Times are **CDT**.

**Only four things change between shifts.** Everything else — shapes, gate authority, the
mandatory lines, the run object, the comms vocabulary — is identical in every shift. That
sameness is the point of the skill.

| | **Night** 22:00 -> morning | **Afternoon** 11:00 -> 17:00 | **Evening** 18:00 -> 22:00 | **Morning** ~10:00 |
|---|---|---|---|---|
| Pings | **none** | ntfy allowed; informational only, never permission-blocking | none (owner present) | n/a |
| Blockers | ledger the blocker, **reroute** to the next row, never stop | ping ntfy once, **continue** | ask the owner in-channel | attended |
| Scope | full queue, up to 4 builders | full queue | **short work** — 1-2 rows per lane, gate-heavy | no build |
| Typical shape | ABCD / ABCDE | ABC / ABCD | AB / ABC | runs `/run-builder --shift afternoon` |
| Owner acts | pastes at 22:00 | pops in if free; 17:00 check-in | 22:00 launches Night | reviews Night, preps Afternoon |

## Night (22:00 -> morning)

Owner is **completely unavailable**. The run must never need him.

- **No pings of any kind.** Not ntfy, not anything.
- A blocker is **ledgered and rerouted**: write the blocker with its evidence into
  `runs/run-NN/evidence/<lane>/BLOCKED-<row>.md`, post `BLOCKED` on the run channel, then take
  the **next row in your queue**. A lane never stops on a blocker.
- **Forbidden in Night, absolutely:** anything requiring an owner ruling, and any deploy.
  Deploy is always the owner's attended act. Findings are not authorization — in any shift, but
  Night is where that rule gets tested.
- A row that turns out to need a ruling is written into `OWNER-QUESTIONS.md` and abandoned for
  the run. It is not guessed at.
- A Night lane never addresses the owner, in any channel, by any mechanism.

## Morning (~10:00, attended)

Not a build shift. The owner's ritual, in this exact order:

1. `runs/run-NN/REPORT.md`
2. `runs/run-NN/OWNER-QUESTIONS.md` — he writes into the blank `## RULINGS` section
3. `runs/run-NN/next-shift/PROMPTS.md` — he pastes

Then he runs `/run-builder <shape> "<theme>" --shift afternoon` (or accepts the shape the Night
gate proposed in `next-shift/RUN.md`). Review, feedback, paste. That is the whole check-in.

## Afternoon (11:00 -> 17:00)

Owner is around but not watching. This is the only shift where a ping is legal.

- **ntfy ping: informational only, never permission-blocking.** A lane that pings then waits has
  violated the shift. Ping, then **continue**. Mechanical test: the tool call immediately after
  the ping must be the next row's first action. No sleep, no inbox poll for a reply, no re-read
  of the ntfy config. If your next action is anything else, you have blocked on a ping.
- One ping per blocker. Not per row, not per commit, not a progress tick.
- Ping only on **completion or blockage/failure**. Config is read at
  `<hub>\00-Inbox\_Review\fleet-notify.local.json`; prefer the wired sender
  `fleet-ntfy-notify.ps1`, which resolves the config itself and never prints the topic.
- Body rules: **one line**, lead with the outcome, name the artifact path. **No secrets, no
  client PII, no money figures** — the topic is an unauthenticated credential and it appears in
  no tracked file. Never embed server or topic values in a prompt, a run object, or this skill.
- 17:00 is a check-in, same three-file ritual as Morning.

## Evening (18:00 -> 22:00)

Owner present. Short work, gate-heavy.

- **1-2 rows per lane.** `AB` or `ABC`. The gate does proportionally more.
- No pings — ask the owner in-channel; he is there.
- Its real job is to leave the Night run composed: the final turn writes
  `next-shift/PROMPTS.md` for the 22:00 Night launch.
- At 22:00 the owner launches Night.

## The final turn of every shift (the only automation)

At `--stop-at` minus 20 minutes the **gate lane** stops verifying and writes:

```
runs/run-NN/next-shift/PROMPTS.md   paste-ready prompts for the next shift run
runs/run-NN/next-shift/RUN.md       proposed shape + theme + MUST-MEET legs
runs/run-NN/HANDOFF.md              gotchas + what was verified (next run MUST NOT re-verify it)
runs/run-NN/REPORT.md               what shipped; numbers re-read from artifacts at write time
runs/run-NN/OWNER-QUESTIONS.md      decisions needed, with a blank ## RULINGS section
```

Then `close-run.ps1`: tag `run-NN-close` at a named commit, flip the LEDGER row, delete scratch
and **verify the deletion**, emit `evidence/gate/CONFORMANCE.json`.

**Shift succession:** Night -> Morning -> Afternoon -> Evening -> Night. The gate proposes the
next shift's shape in `next-shift/RUN.md`; the owner may override it at the check-in.

## No cron, in any shift

There is no cron registration for shift transitions and no recovery cron. There are zero
recorded successful automated recoveries. Recovery is the owner re-pasting from
`runs/run-NN/prompts/PROMPT-<X>.md` — which is precisely why prompts are files.
