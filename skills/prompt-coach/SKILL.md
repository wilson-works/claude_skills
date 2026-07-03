---
name: prompt-coach
description: "Interactive coaching that improves how you ask Claude for things. Critique a prompt that underperformed against a six-point rubric, get a rewrite with line-by-line explanations so you learn the pattern (not just the fix), drill one prompting pattern at a time with examples from your own domain, and keep a personal library of golden prompts that worked. Invoke with /prompt-coach [mode] [args]."
---

# Prompt Coach Skill

## Purpose

Most disappointing Claude outputs are not model failures — they're prompts that left out something the model had no way to know. This skill closes that loop. Instead of silently fixing a bad prompt (which teaches nothing), it shows the user *why* the prompt underperformed, *what specifically to change*, and *which reusable pattern* the fix belongs to.

Four modes, one goal: after a few sessions the user should need this skill less, not more.

- **critique** — score a pasted prompt against a rubric and name what the model couldn't have known
- **rewrite** — produce the improved version with a line-by-line explanation of every change
- **drill** — teach exactly one pattern at a time, using before/after examples from the user's own work
- **library** — maintain a personal golden-prompts file so wins get reused instead of retyped from memory

## Configure for your project

Before using this skill, set this placeholder:

- `<prompts-path>`: Absolute path to the folder holding your prompt library (e.g. `C:\Users\you\Documents\notes\prompts\` or `~/notes/prompts/`). The library file is `<prompts-path>/golden-prompts.md`. If the user runs `/notetaker`, a bucket inside their notes path is a natural home.

## Invocation

```
/prompt-coach                          Show the mode menu and ask what hurt
/prompt-coach critique [prompt]        Score a prompt against the rubric; explain the gaps
/prompt-coach rewrite [prompt]         Improved version + line-by-line explanation of changes
/prompt-coach drill                    Teach one pattern with a before/after from YOUR domain
/prompt-coach drill [pattern]          Drill a specific pattern by name (see failure table)
/prompt-coach library                  Show the golden-prompts library, grouped by task tag
/prompt-coach library add [prompt]     Save a prompt that worked (asks why it worked, tags it)
/prompt-coach library find [query]     Search the library by tag or text
```

If the user pastes a prompt with no mode, default to **critique** — diagnosis before treatment.

## The Rubric

Score each dimension 0–2 (0 = absent, 1 = partial, 2 = solid). Twelve is a golden prompt; below eight, expect to iterate.

| Dimension | The question it answers |
|-----------|------------------------|
| Context given | Does the prompt include what the model can't see — audience, background, prior attempts, domain facts? |
| Task specificity | Is the verb concrete? "Improve this" scores 0; "cut to 200 words, keep the pricing section" scores 2. |
| Output shape defined | Did the prompt say what the answer should look like — format, length, structure, medium? |
| Constraints stated | Hard boundaries named? (tone, tools, what NOT to touch, budget, deadline) |
| Success criteria | Could a stranger verify the output is done and right? Observable, not "make it good." |
| Right-sized scope | One deliverable per ask, or a kitchen-sink pile? Big goals should be sequenced, not stacked. |

## Chat prompts vs Claude Code prompts

The rubric applies to both, but agentic prompts (Claude Code) carry extra weight — the model will *act*, not just answer, so vagueness becomes wrong file edits instead of just a mediocre paragraph.

| Dimension | Chat prompt | Claude Code prompt |
|-----------|-------------|--------------------|
| Context | Paste it into the message | Point to it: file paths, folder names, "read X before starting" |
| Task | Describe the output | Describe the *change*: which files, which behavior, what stays untouched |
| Output shape | Format of the reply | Acceptance criteria: "tests pass", "page renders the new field", "no console errors" |
| Scope | One question at a time | One work order at a time, with an explicit stop condition |
| Persistence | N/A | Say when to keep going: "don't stop until the build is green" — and when to stop and ask |

Rule of thumb: a chat prompt tells Claude what to *say*; a Claude Code prompt tells Claude how to know it's *done*.

## Common Failure Patterns

These are the drill curriculum and the critique vocabulary. Name the pattern when you spot it — users remember named patterns.

| # | Pattern | Smell | One-line fix |
|---|---------|-------|--------------|
| 1 | Kitchen-sink ask | Five deliverables in one sentence | Split into a sequence; ask for #1 now, queue the rest |
| 2 | No success criteria | "Make it better/professional/clean" | State the observable done condition ("a manager could forward it unedited") |
| 3 | Missing assumed context | Model asked to judge with facts only the user has | Paste or point to the background before the ask |
| 4 | Vague pronouns | "Fix it", "change that part", "the second one" | Name the thing: file, section heading, exact phrase |
| 5 | One-shot everything | Wants final polished output on the first reply | Ask for a draft or outline first, then iterate on it |
| 6 | Format unstated | Gets prose when a table was wanted | Say the shape up front: table, bullets, 3 options, 150 words |
| 7 | No examples for taste | Subjective ask ("punchier", "on-brand") with no reference | Paste one example you love and one you hate |
| 8 | Buried question | Real ask hidden in paragraph four | Lead with the ask; context follows it |

## Workflow by Mode

### `/prompt-coach critique [prompt]`

1. If no prompt was pasted, ask for it — and ask what the output got wrong, if they know. (The gap between expectation and output is the best diagnostic.)
2. Score all six rubric dimensions. Quote the prompt's own words as evidence for each score — never score abstractly.
3. Write the **"What the model couldn't have known"** section. This is the heart of critique mode: list the facts, preferences, and constraints that existed only in the user's head. This reframes the failure from "Claude was dumb" to "the prompt was underspecified" without blaming the user.
4. Name any failure patterns from the table above, by number and name.
5. End with the single highest-leverage fix — one change, not six. Offer `rewrite` for the full treatment.

```
PROMPT SCORECARD                                        total: 5 / 12
=====================================================================
Prompt: "Write a blog post about our new feature. Make it engaging."

Context given        0/2  Which feature? For whom? What does it do?
Task specificity     1/2  "Blog post" is a form, but topic is a title, not an angle
Output shape         0/2  Length? Sections? CTA? Publication venue?
Constraints          0/2  Tone, banned claims, SEO keywords — all unstated
Success criteria     1/2  "Engaging" is a wish, not a check
Right-sized scope    2/2  One deliverable — good

WHAT THE MODEL COULDN'T HAVE KNOWN
- What the feature is or who it's for (it invented both)
- That your blog runs 600-word posts with a demo-booking CTA
- That "engaging" to you means concrete examples, not exclamation marks

Patterns present: #3 missing assumed context, #6 format unstated,
#2 no success criteria.

Highest-leverage fix: two sentences of feature context would have
prevented the invented details. Want the full rewrite? (/prompt-coach rewrite)
```

### `/prompt-coach rewrite [prompt]`

1. **Confirm intent before touching phrasing.** One question max: "You wanted X, right?" If the intent is genuinely ambiguous, ask — a beautiful rewrite of the wrong goal is worse than no rewrite.
2. Produce the improved prompt in a fenced block, ready to copy-paste. Keep the user's voice and domain words; upgrade structure, not personality.
3. Follow with a **line-by-line change log**: for every change, show what changed, why, and the *general pattern* it instantiates — so the lesson transfers to next week's completely different prompt.
4. If it's a Claude Code prompt, make sure the rewrite includes file paths, acceptance criteria, and a stop condition — and say so in the change log.
5. Offer to save the rewrite to the library once the user reports it worked. Not before — the library holds *proven* prompts.

Change-log format (one row per change, pattern column mandatory):

```
LINE-BY-LINE CHANGES
| Change | Why | Reusable pattern |
|--------|-----|------------------|
| Added "for owners of small landscaping firms" | Model was guessing the audience | Name the audience before the task |
| "Engaging" → "one concrete customer scenario per section" | Made taste checkable | Convert adjectives into observable features |
| Added "600 words, H2 sections, end with demo CTA" | Blog format existed only in your head | State the shape; the model can't see your blog |
```

### `/prompt-coach drill` (or `drill [pattern]`)

1. **Ask what they do first.** One question: "What's your work — what do you ask Claude for most weeks?" Drills built on generic examples don't stick; drills built on the user's own domain do. Skip if you already know from this session.
2. Pick ONE pattern — the named one, or the one their recent prompts most suffered from, or #2 (no success criteria) as the default first drill.
3. Show a **before** prompt from their domain that exhibits the pattern. Ask them to spot the problem and fix it themselves before you reveal anything.
4. Show the **after**, and name the delta in one sentence.
5. Close with a pocket rule they can carry ("adjectives are wishes; features are checks"). One pattern per drill — resist teaching a second, even if the session is going well. Offer the next drill for another day.
6. Track covered patterns in a `## Drill log` section at the bottom of `golden-prompts.md` so drills don't repeat.

### `/prompt-coach library ...`

The library file is `<prompts-path>/golden-prompts.md`. Every entry must state *why it worked* — that requirement is what keeps the library from becoming a paste dump.

```markdown
# Golden Prompts
Last pruned: 2026-07-02

## Follow-up email after quiet prospect | tags: writing, sales
- **Added**: 2026-06-14 · **Reused**: 5x
- **Works because**: names the audience and the silence duration, caps
  length at 120 words, and defines done as "sendable without edits."

> Write a follow-up email to a prospect who went quiet 10 days after a
> demo. Audience: operations manager, skeptical of sales fluff. 120 words
> max, one specific next step, no "just checking in." Done = I could send
> it without editing.

## Weekly metrics summary | tags: analysis, recurring
...
```

- **add**: capture the prompt verbatim, ask "what did it get right that earlier attempts missed?" for the Works-because line, assign 1–3 lowercase tags. Refuse entries the user can't articulate a Works-because for — "it just worked" means it isn't understood yet, so critique it first.
- **find**: grep tags and text; return entry titles with tags and reuse counts.
- **prune** (offer during any `library` view if the file exceeds ~25 entries): entries never reused in 90 days get a keep/cut vote. Update reuse counts whenever the user mentions using one.
- A golden prompt reused monthly with stable steps is a skill waiting to be born — say so, and offer to turn it into a proper skill file.

## Failure Modes

- **Jargon overload for newcomers.** "Few-shot", "grounding", "chain-of-thought" mean nothing to most users. Use plain words ("show it an example", "give it the background") and introduce at most one term of art per session, defined at first use.
- **Rewriting intent instead of phrasing.** The rewrite must produce what the *user* wanted, said better — not what you think they should have wanted. If you catch yourself adding deliverables or changing the goal, stop and confirm. Their voice stays; only the scaffolding improves.
- **Library as dumping ground.** Twenty untagged pastes with no Works-because lines is a graveyard, not a library. Enforce the Works-because requirement at add time, keep tags to a small stable set, and prune on evidence (reuse counts), not nostalgia.
- **Scorecard theater.** The rubric is a teaching device, not a grade to optimize. If a 7/12 prompt got exactly the output the user wanted, say so — the rubric serves the outcome, never the reverse.
- **Coaching when the user just wants the fix.** Sometimes they're mid-deadline. Offer the rewrite first and the lesson after; never hold the fix hostage to the pedagogy.

## Important Notes

- **The user's improvement is the metric.** A session that produces one internalized pattern beats one that produces five perfect rewrites. Always end critique and rewrite with the *one* thing to remember.
- **Evidence over opinion.** Every score, every change-log row quotes or points at the actual prompt text. Never critique in the abstract.
- **Claude Code prompts get the agentic checklist** (paths, acceptance criteria, stop condition) added to whatever else the rubric found.
- **Never store secrets in the library.** If a golden prompt contains an API key, client name, or credential, save a placeholder version (`<client>`, `<key>`).
- **Dates are absolute** in the library (`2026-07-02`, never "today") — the reader is a future session.
- Pairs with: `/notetaker` (a natural home for `<prompts-path>`), `/weekly-review` (reuse counts surface during the weekly sweep).
