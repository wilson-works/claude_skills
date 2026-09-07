# Model & Effort Routing

How this skill pack decides **which Claude model does which job**. The orchestration
skills (work-orders, marathons, councils, agent-org) follow these conventions.

Verified against code.claude.com docs, 2026-09-07:
[model-config](https://code.claude.com/docs/en/model-config.md) ·
[sub-agents](https://code.claude.com/docs/en/sub-agents.md).

## The model aliases

| Alias | Resolves to | Context | Use for |
|---|---|---|---|
| `opus` | Claude Opus 5 (`claude-opus-5`) | 1M native | Architecture, review gates, deep research, judgment under ambiguity |
| `sonnet` | Claude Sonnet 5 (`claude-sonnet-5`) | **1M native** | Implementation, refactors, context briefs, batch execution — the default worker |
| `haiku` | Claude Haiku 4.5 (`claude-haiku-4-5`) | 200K | Mechanical steps: formatting, log scans, cheap gates |
| `fable` | Claude Fable 5.1 (`claude-fable-5-1`) | 1M native | Review gates at both ends of a run, and the orchestrator on a Fable lane |
| `best` | Latest Fable where available, else `opus` | — | "The strongest thing you have" — non-reproducible by design |
| `default` | Clears the override; account-type default | — | Undoing a session-scoped `/model` change |
| `opusplan` | Opus in plan mode → Sonnet in execution | — | Hybrid interactive work |
| `inherit` | The parent session's model | — | Skills/agents that shouldn't change the caller's tier |

Sonnet 5 has 1M context natively — long marathon lanes no longer thin out on Sonnet
workers. `[1m]` on Sonnet 5 is therefore redundant, but it is still valid syntax and
still meaningful on models that are not 1M-native, so never strip it as a "fix".
Context discipline (`/caveman`, one-line comms reads) still pays: you're billed
for what you carry.

## The routing rule

**Opus decides, Sonnet ships, Haiku sweeps.**

| Role in a run | Model |
|---|---|
| Review / merge gate (John) | `opus` (at `effort: xhigh` — one cranked review per WO is the cheapest quality you can buy) |
| Orchestrator on a Fable lane; the compose and close gates of a run | `fable` — the highest output price in the lineup ($50/MTok out against Opus 5's $25, per [pricing](https://platform.claude.com/docs/en/about-claude/pricing)), so spend it where one call decides the shape of many, never per work order |
| Implementers (juniors, work-order agents) | `sonnet` — escalate a task to Opus only after it fails on Sonnet |
| Deep research synthesis (marathon-research) | `opus` |
| Scope checks, context briefs, distill/split passes | `sonnet` at `effort: low`/`medium` |
| Council/premortem advisors (breadth work) | `sonnet`; the chairman synthesis gets `opus` |
| Log collation, formatting | `haiku` |

## Where routing lives (precedence — highest wins)

1. `CLAUDE_CODE_SUBAGENT_MODEL` **paired with `CLAUDE_CODE_SUBAGENT_MODEL_FORCE=1`** —
   together they override every subagent's model, frontmatter included. The budget lever,
   and it needs both vars (v2.1.257+).
2. The `model:` parameter on an individual Agent call (the Agent tool has no `effort` parameter; effort comes from the agent file or the session) (how the marathon
   skills route).
3. The agent file's `model:` / `effort:` frontmatter (this pack's standing assignments).
4. `CLAUDE_CODE_SUBAGENT_MODEL` **without FORCE** — it sits here, *below* frontmatter, as
   of Claude Code v2.1.251. So on its own it does nothing to any agent that declares a
   `model:`, which in this pack is all of them.
5. The main session model.

Measured 2026-09-07 on Claude Code 2.1.263: three headless runs spawning
`head-claude-clay` (frontmatter `model: opus`) and asking it to report its own model
ID. With `CLAUDE_CODE_SUBAGENT_MODEL=sonnet` alone Clay ran `claude-opus-5[1m]` —
**identical to the control run with the var unset**. Only with
`CLAUDE_CODE_SUBAGENT_MODEL_FORCE=1` added did Clay run `claude-sonnet-5`. Set the model var
alone and nothing errors — you simply pay full rates for a night you believe is cheap.

Skills can also pin `model:`/`effort:` in SKILL.md frontmatter — a one-turn override.

**Effort has its own ladder**, separate from the model one. The levels are `low` `medium`
`high` `xhigh` `max`, defaulting to `high` on every model that supports effort except Opus
4.7 (`xhigh`). With `ultracode` off, Claude Code takes the first of these that applies:
(1) an explicit choice — `CLAUDE_CODE_EFFORT_LEVEL`, `--effort` at launch, or `/effort`
in-session; (2) **a held model default on Fable 5, Opus 4.8 and Opus 4.7 only** — from the
first run of one of those, that model's default effort holds across sessions *even when
your settings resolve a different level*, until you change effort once interactively
(Opus 5 and Fable 5.1 have no such hold, and this rung is why a settings pin can look
ignored); (3) your settings — the level saved for that model, or an `effortLevel` key,
with `modelSettings` stating the precedence between them; (4) the model's own default.
The per-model `modelSettings` block is still the only way to pin effort per tier without
editing every agent file.

`ultracode` is **not** an effort level — the docs call it "a Claude Code setting rather
than a model effort level". It sends `xhigh` and additionally has Claude orchestrate
dynamic workflows. Set it with `/effort ultracode`, `--effort ultracode` (v2.1.203+),
`"ultracode": true`, or the `/model` picker; the persisted `effortLevel` setting and
`CLAUDE_CODE_EFFORT_LEVEL` do not accept it.

## Two rules of thumb

1. **Never route a task to Opus that has not failed on Sonnet** — unless it's a review
   gate, cross-source synthesis, or an irreversibility decision. (`/marathon-orders` is
   the deliberate exception: its queue is depth work by definition.)
2. **A cheaper front-runner protects the expensive pass.** Sonnet scope-check before the
   Opus researcher; Sonnet context brief before the executor. Never cold-start an
   expensive agent on work a cheap summary could frame.

Version floors: `effort:` frontmatter needs Claude Code v2.1.145+, subagent `memory:`
needs v2.1.196+. Both are ignored harmlessly on older versions.
