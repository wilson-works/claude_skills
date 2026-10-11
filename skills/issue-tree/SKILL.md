---
name: issue-tree
description: "Breaks a problem into the right issue tree before anyone studies it: Why when the cause is unknown (testable hypotheses), What when a deliverable needs a plan (a sequenced workplan), How when the goal is set (ranked options). Picks the tree type and says why, builds it level by level, and runs a MECE pass on every level that names one overlap and one gap, or says it looked and found none. Skip for: stress-testing a finished plan (use /premortem) or generating ideas (use /brainstorm). Invoke with /issue-tree [problem]."
---

# Issue Tree

## Purpose

Many problems go wrong before anyone studies them. One question quietly asks for a cause, a plan and a solution at once, and each person answers a different one. This skill makes the job explicit first (find causes, break down work, or list paths), then builds that one tree and checks every level for overlap and gaps.

You name the problem and prune the branches. The skill picks the tree type, drafts the branches and runs the checks, the same way every time.

## Invocation

```
/issue-tree <problem>               Pick the tree type, build it, run the MECE pass per level
/issue-tree <problem> --type why    Use the named type (why | what | how) instead of picking one
```

## Step 1: Pick the tree type and say why

| The team needs... | Tree | The root asks | Leaves are | Output |
|---|---|---|---|---|
| the cause of something it can see | **Why** | Why is X happening? | candidate causes | testable hypotheses |
| a plan for a deliverable | **What** | What does producing X require? | analyses, decisions, commitments, artifacts | a sequenced workplan |
| ways to reach a goal it has chosen | **How** | How might we reach X? | concrete actions | ranked options |

State the choice in one sentence with its reason, for example: "Why-tree: the team knows activation is low but not the cause. A How-tree fits once a cause is confirmed." Done when the user accepts the type or names another.

## Step 2: Build it one level at a time

1. Write the root as one question. Done when the user agrees it is the problem.
2. Draft 3–5 branches for the level, each a distinct line of inquiry.
3. Run the MECE pass on the level (Step 3) before going a level deeper.
4. Stop at leaves someone can test (Why), schedule (What) or choose (How); two or three levels is usually enough.
5. In a What-tree, tag each leaf `[ANALYSIS]`, `[DECISION]`, `[COMMITMENT]` or `[ARTIFACT]`, and order the leaves so each depends only on earlier ones.
6. Close with the output the tree type promises: hypotheses with the cheapest test first, a sequenced plan, or ranked options.

## Step 3: The MECE pass, on every level

MECE means mutually exclusive (no two branches cover the same ground) and collectively exhaustive (together they answer the root). For each level, write both lines:

```
MECE level N — overlap: <the two branches that cover the same ground, and the fix>
               gap: <what no branch covers, and the branch that would cover it>
```

Name one overlap and one gap, or write "looked, found none" for either. A level is done only when both lines are written.

## Example (synthetic)

```
/issue-tree "Trial sign-ups doubled but paid conversions stayed flat"
TYPE: Why-tree. The result is known and the cause is not; a How-tree fits once a cause is confirmed.

WHY: Why did paid conversions stay flat while trial sign-ups doubled?
├── 1. The new trials are a different audience
│   ├── 1.1 The new channel brings students, not teams
│   └── 1.2 The new landing page promises a free tier that does not exist
├── 2. The trial never shows the paid value
│   ├── 2.1 The paid feature is hidden until day 10
│   └── 2.2 Onboarding ends before the first report is built
└── 3. Something blocks the purchase step
    ├── 3.1 Checkout fails for cards issued outside the US
    └── 3.2 Pricing changed the same week
MECE level 1 — overlap: 1.2 and 3.2 both turn on how the price reads; move 1.2 under 3 as "price unclear before checkout"
               gap: nothing covers measurement; add 4 "conversions are undercounted (trial and paid tracked in different tools)"
MECE level 2 — overlap: looked, found none
               gap: branch 2 has no sales-assisted path; add 2.3 "large accounts wait for a sales call that never comes"

OUTPUT: testable hypotheses, cheapest test first
  H1 conversions are undercounted → compare one week of billing records with the analytics count
  H2 checkout fails outside the US → read the payment provider's decline log by country
  H3 the paid feature is found too late → compare conversion for trials that opened it before and after day 10
```

## Failure Modes

- **Picking the tree by habit.** A Why-tree on a problem whose cause is known wastes the session; a How-tree before the cause is known ranks fixes for the wrong problem. Step 1's sentence names the reason; when the reason is thin, ask.
- **Branches that reword one idea.** That is an overlap, and the MECE pass names it.
- **A blank MECE line.** "Looked, found none" is an answer; an empty line is a skipped check.
- **Leaves nobody can act on.** "Improve the product" is not a leaf. Stop where a leaf can be tested, scheduled or chosen.
- **Treating a clean pass as truth.** The MECE pass checks structure, not facts. Each Why leaf stays a hypothesis until its test is run.

## Important Notes

- **The user owns the problem.** The skill drafts; the user names the root, accepts the type and prunes branches.
- **One tree per run.** When the problem needs a second tree (a Why that confirms a cause, then a How), finish the first and offer the second.
- Pairs with: `/premortem` (stress-test the plan a What- or How-tree produced), `/brainstorm` (widen a How-tree's options), `/llm-council` (choose between ranked options), `/decision-policy` (record the choice).
