---
name: reverse-doc
description: "Generates missing design/architecture documentation from existing code. Reads implementation, asks clarifying questions about intent, then produces spec documents for systems that shipped without written specs. Invoke with /reverse-doc [system|feature-name|file-path]."
---

# Reverse Doc Skill

## Purpose

Many features get built fast without a written spec. When revisiting them, onboarding a new contributor, or migrating to a knowledge base, there's no documentation trail. This skill works backwards: reads the current code, asks clarifying questions about design intent, and produces a spec document. The intent-clarification step is critical — code alone can't distinguish intentional design from accidental behavior.

## Configure for your project

Before first use, replace the following placeholders:

- `<project-root>` — absolute path to your project
- `<core-package-path>` — path to the module that owns business logic (e.g. `src/lib/`, `packages/core/src/`)
- `<src-path>` — path to your application code (e.g. `src/`, `apps/web/src/`)
- `<reverse-specs-path>` — where generated specs are saved (e.g. `docs/specs/reverse/`, `design/reverse-specs/`)
- `<existing-design-docs>` — paths to any existing design docs (e.g. `DESIGN.md`, `ARCHITECTURE.md`)
- `<memory-path>` — path to long-running project memory or notes (optional)

## Invocation

```
/reverse-doc auth                                 - document the auth system
/reverse-doc <core-package-path>/billing.ts        - document a specific file
/reverse-doc Onboarding Wizard                    - document a named feature (fuzzy match)
/reverse-doc rate-limits                          - document the rate-limit module + related
/reverse-doc --audit                              - scan all core modules, list ones lacking docs
```

## Prerequisites

- File read access to `<project-root>`
- Write access to `<reverse-specs-path>`

## Workflow

### Step 1: Identify Target

Based on arguments:

- **System name**: Map to relevant source files. Build a known-mapping table for your project, or grep for the term across `<core-package-path>` and `<src-path>`.
- **File path**: Document that specific file
- **Feature name**: Grep for references; if ambiguous, ask user to pick
- **--audit**: List all modules in `<core-package-path>` that lack any reference in `<existing-design-docs>` or `<reverse-specs-path>`

### Step 2: Scan Implementation

Read the target files. Extract:

- **Exported functions/constants**: name, signature, purpose inferred from usage
- **Constants / thresholds**: hard-coded values (e.g., timeouts, rate limits, default config)
- **Formulas**: any mathematical computations with their inputs and outputs
- **Branches / rules**: conditional logic (e.g., "if user role is admin, skip the cap")
- **Dependencies**: imports from other modules, data stores or external services touched
- **Side effects**: what gets written, fired, or triggered

Also check for:
- Any existing doc comments (`/** ... */` or equivalent) in the code
- Related entries in `<existing-design-docs>` or `<memory-path>`
- Tests that document expected behavior

### Step 3: Infer Intent (Surface Uncertainty)

From the scanned data, draft:

- **Purpose statement** (best guess)
- **Key design decisions** (as inferred from constants and branches)
- **Assumptions** (what the code implies about the expected use case)

For each, identify what's **clear from code** vs **unclear without asking**. Examples:

Clear:
- "Retry policy is 3 attempts with exponential backoff — verifiable from retry.ts"
- "Default page size is 25 — hardcoded constant"

Unclear:
- "Is the upload cap of 10MB a security measure, a cost control, or a UX guess?"
- "Function X has a 24h cache TTL with 3x the normal weight — was this a deliberate tradeoff or an arbitrary value?"

### Step 4: Ask Clarifying Questions

Present the unclear items to the user, concisely. Batch questions so the user can answer in one round. For each:

- What you found in code
- Why you think it matters for the doc
- The specific intent question

Example:
```
Q1: `MAX_UPLOAD_BYTES = 10_000_000` in upload.ts
    No corresponding rationale in existing docs.
    Was 10MB chosen because (a) bandwidth/cost, (b) abuse prevention, (c) UX (avoid long waits), or (d) arbitrary?

Q2: The handler always processes "primary" attachments before "secondary".
    Is that order intentional (priority), or incidental (implementation order)?
```

Keep to 2-5 questions per document. If the code is clear enough, skip this step.

### Step 5: Draft the Document

Produce the spec using this template:

```markdown
---
status: reverse-documented
source: [file paths]
generated: [date]
confidence: high | medium | low (based on how much required guessing)
---

# [System Name]

## Status
Reverse-documented from existing implementation on [date]. Intent clarified via [interview | inferred from code + memory].

## Purpose
[one paragraph: what this system does and why it exists]

## Key Constants
| Name | Value | Source | Rationale |
|------|-------|--------|-----------|
| MAX_UPLOAD_BYTES | 10_000_000 | upload.ts | [reason from clarification] |
| RETRY_ATTEMPTS | 3 | retry.ts | [reason] |
[...]

## Formulas
### [Formula name]
`outputForInput(x) = f(x)`

Variables:
- `x`: range and meaning
- Output: meaning

Rationale: [from clarification]
Example: f(10) = ...

## Rules / Branches
- **Admin override**: caps skipped when `role === 'admin'`
- [...]

## Dependencies
- Reads from: [data stores, other modules, external APIs]
- Writes to: [...]
- Triggers: [background jobs, events, UI updates]

## Known Interactions
- [With other system A: ...]
- [With other system B: ...]

## Open Questions
- [anything the clarification step left unresolved, flagged for future]

## Revision History
- [date]: Reverse-documented from HEAD [commit SHA]
```

### Step 6: Write and Link

Save to `<reverse-specs-path>/[system-name].md` or merge into an existing doc in `<existing-design-docs>` if the system already has a short entry there.

If the clarification surfaced facts worth persisting, offer to save a project memory note.

### Step 7: Follow-Up

- If --audit mode: list all undocumented systems and offer to batch-document them
- Recommend a systems/architecture diagram update to place the newly-documented system in the larger graph
- If the doc surfaced design smells (e.g., hardcoded values that should be config), offer to file a tech-debt work item

## Principles

- **Clarify before writing.** Code can't distinguish intent from accident. The clarification step is non-optional for confidence=high docs.
- **Cite the source.** Every stated behavior points to a specific file plus line.
- **Confidence is a feature.** Mark low-confidence docs as such; don't pretend the doc is authoritative when it's partially inferred.
- **One system per doc.** Don't try to reverse-doc multiple systems in one file.
- **Never invent behavior.** If the code doesn't specify it, the doc says "not specified" rather than guessing.

## Anti-Patterns

- Do not copy doc-comments verbatim into the spec; synthesize.
- Do not document code that's known to be wrong or pending removal. Ask first.
- Do not skip the clarification step for systems with hardcoded magic numbers.
- Do not update existing canonical design docs without the user's approval; propose changes first.
