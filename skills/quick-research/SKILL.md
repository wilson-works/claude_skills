---
name: quick-research
description: "Single-session cited research for short-but-complex on-the-job questions. Same hard rules as marathon-research — every claim carries a verifiable URL, unclear scope fails fast, no bluffing — at 5–20 minute scale with an inline answer. Invoke with /quick-research [question] [--file] [--sources N]."
---

# Quick Research Skill

## Purpose

For the question that lands mid-workday: too complex for a one-shot answer from memory, not worth an 8-hour `/marathon-research` run. Comparable rigor, single-wave scale: scope-gate the question, search the live web, and return an answer where **every factual claim carries a URL you can click and check**.

The contract is trust: an answer from this skill is safe to forward to a client, cite in a memo, or act on — because anything that couldn't be verified was dropped or explicitly marked unresolved, never bluffed.

### When to use which

| | `/quick-research` | `/marathon-research` | `/deep-research` |
|---|---|---|---|
| Shape | One question, now | Queue of topics, unattended | One big topic, deep dive |
| Duration | 5–20 min | 4–8 h (cron loop) | 30–90 min |
| Output | Inline answer (file optional) | Report folders + index | Cited report file |
| Sources | 3–10 | 15–40 per topic | 10–25 |
| You present? | Yes — can answer clarifying questions | No — unclear scope hard-fails | Yes |

Rule of thumb: if the answer fits on one page and you need it today, it's quick-research.

## Configure for your project

- `<research-root>` — only needed for `--file` mode: where saved answers go (e.g. `<project-root>/research/quick/`). Inline mode needs no configuration.

## The Hard Rules

Inherited from marathon-research, adapted for an attended single session. These are inviolable — they are the entire difference between this skill and "just asking."

1. **Every factual claim carries a verifiable URL.** Inline link or footnote — no exceptions, including "well-known" facts that anchor the answer. A claim you cannot source gets dropped, or explicitly listed under **Unresolved** — never stated bare.
2. **If the scope is unclear, STOP and ask — before any searching.** The user is present (unlike marathon), so unclear scope means one round of clarifying questions, not a silent guess. If it's still ambiguous after one round, state the interpretation you're taking and proceed under it, flagged at the top of the answer.
3. **No bluffing, ever.** If the web doesn't answer the question, the deliverable is "here's what I could and couldn't establish" with sources for the *could* part. A partial honest answer beats a complete invented one.
4. **Stay inside the time box.** This is a 5–20 minute skill: **5–15 WebSearch/WebFetch calls total.** If the budget is spent and the question isn't answered, report what you have + what a longer run would chase — and offer to queue it for `/marathon-research`.
5. **Self-validate before returning.** Re-read the draft answer claim by claim; every factual sentence has a URL or a footnote, every footnote resolves. This is the same check marathon-research runs as an orchestrator-side validator — here you ARE the validator.

## Invocation

```
/quick-research [question]             Research and answer inline
/quick-research [question] --file      Also save the answer to <research-root>
/quick-research [question] --sources N Require at least N independent sources (default 3)
/quick-research --escalate             Convert the current question into a marathon-research queue entry
```

## Workflow

### Step 1 — Scope gate (HARD RULE #2)

Before searching, classify the question:

- **Clear**: you can state what a complete answer contains. Proceed.
- **Ambiguous**: multiple materially different readings ("best CRM" — for whom? what size? what budget?). Ask **one round** of clarifying questions (max 3, one message). Then proceed under the answers, or under a stated interpretation.
- **Not a research question**: opinions about the user's own situation, math, anything answerable from files on disk — say so and answer directly without the research apparatus.

Also set the **freshness requirement** now: does this need current data (prices, versions, laws, people-in-roles)? If yes, sources must be dated or verified-current; note retrieval date in the answer.

### Step 2 — Plan the searches

Decompose into 2–4 sub-questions max. For each, note the search angle and the kind of source that would settle it (official docs beat blogs; primary beats aggregator). Don't show this plan unless asked — just execute it.

### Step 3 — Search and fetch (HARD RULES #1, #4)

- WebSearch to discover, WebFetch to verify. **Never cite a search-result snippet** — fetch the page before citing it (snippets truncate and mislead).
- Prefer primary sources: official documentation, government data, the company's own pricing page, the actual paper, the statute text. Wikipedia navigates; its references are the citation, not the article.
- **Independent corroboration for load-bearing claims**: any figure or fact the whole answer leans on needs 2 independent sources, or gets flagged `(single source)`.
- Dead link / paywall → find an alternative; if none, the claim doesn't make the answer.
- Track the call budget. At ~12 calls, start closing.

### Step 4 — Compose the answer

Format for an inline answer (target: **under 60 lines** — this is a working answer, not a report):

```
ANSWER — [restated question]
============================

**Bottom line:** [1–3 sentence direct answer]

[Supporting detail, organized by sub-question. Every factual sentence
ends with an inline link ([Title](url)) or footnote [^N].]

**Unresolved:** [claims that could not be verified, and why — or "none"]

**Confidence:** [high | medium | low] — [one line: source quality, corroboration,
freshness. e.g. "high — three independent primary sources, all 2026"]

Sources:
[^1]: [Title](url) — retrieved 2026-07-02
[^2]: ...
```

With `--file`: also write `<research-root>/YYYY-MM-DD-<slug>.md` with the same content. Keep it under 150 lines — the 750-line marathon cap scaled to this skill's size.

### Step 5 — Self-validation pass (HARD RULE #5)

Before sending, verify: every factual sentence has a URL/footnote (drop or move to Unresolved any that don't) · every footnote resolves to a real fetched source · freshness-sensitive claims have dates · the bottom line is actually supported by the cited sources, not by vibes. Only then return the answer.

### `--escalate`

When the question outgrows the time box: write the question plus everything learned so far (sub-questions, promising sources, dead ends) as a `## `-heading entry in the user's marathon-research queue file, framed so the Sonnet scope-gate will pass it. Tell the user it's queued and how to launch: `/marathon-research --queue <path>`.

## Failure Modes

1. **The answer wants to come from memory.** The whole point is verification — memory drafts the search plan, the web supplies the claims. If searching confirms what you expected, great: now it has a URL.
2. **Snippet citation.** Search snippets get facts wrong constantly. Fetch before you cite. No exceptions for "obvious" hits.
3. **Confirmation lock-in.** First plausible source agrees with your prior → you stop looking. For load-bearing claims, deliberately search for the disconfirming angle ("X criticism", "X vs", "X deprecated") before writing.
4. **Scope creep mid-run.** The question mutates while searching ("actually the interesting question is..."). Answer the asked question; note the interesting neighbor under Unresolved or offer a follow-up run.
5. **Budget blown on one stubborn sub-question.** Cap any single sub-question at ~5 calls; mark it unresolved and spend the rest of the budget on the others.
6. **Stale freshness.** A 2023 pricing page answers a 2026 pricing question wrongly. When currency matters and the best source is old, say so explicitly: "as of [date of source] — may have changed."

## Important Notes

- **This skill searches the web every time it runs.** If WebSearch/WebFetch are unavailable in the session, say so and stop — do not degrade into an uncited answer under this skill's name.
- Inline answers follow the user's normal copy-style rules; the structure above is a floor, not a straitjacket — but Bottom line, Unresolved, Confidence, and Sources always appear.
- **Confidence honesty**: "low" is an acceptable grade. A low-confidence cited answer with named gaps is a successful run.
- Multiple questions in one invocation → run them as separate passes with separate answers, or suggest `/marathon-research` if there are more than 3.
- Model routing: runs in the calling session as-is. If dispatched as a subagent from an orchestration skill, route per docs/MODELS.md deep-research row (`opus`, high effort) — synthesis quality is the product.
