---
name: spec-audit
description: "Compares your project's design/spec documents against actual component implementations to detect drift. Finds tokens, rules, or mechanics that diverged between spec and code. Invoke with /spec-audit [tokens|mechanics|all]."
---

# Spec Audit Skill

## Purpose

Spec documents evolve. Components are built to the spec at the time, but later spec updates do not automatically propagate. This skill catches that drift: it scans declared design tokens (colors, fonts, spacing, radii, motion) and any documented rules or mechanics, then grep-verifies them against actual component implementations and source modules. Reports where the spec and code have diverged.

This skill works for any spec-vs-code comparison, including:
- Visual design tokens vs component styles
- Documented rules (copy style, naming conventions, accessibility) vs source
- Documented logic constants/formulas vs implementation

## Configure for your project

Edit these placeholders before running:

- `<SPEC-DOCS>`: list of spec / design doc paths (e.g. `docs/DESIGN.md`, `docs/STYLE-GUIDE.md`, `docs/MECHANICS.md`).
- `<src-path>`: front-end / UI source path (e.g. `src/`, `app/`, `apps/web/src/`).
- `<core-path>`: business-logic source path (e.g. `src/core/`, `packages/core/src/`).
- `<principles>`: project-specific copy/visual rules to lint for (e.g. forbidden words, required tone).

## Invocation

```
/spec-audit              -- full audit (tokens + rules)
/spec-audit tokens       -- just visual design tokens
/spec-audit mechanics    -- just documented logic rules / constants
/spec-audit --fix-easy   -- report mode + offer to auto-fix trivial drift (e.g., color hex updates)
```

## Prerequisites

- File read access to your `<SPEC-DOCS>`
- File read access to `<src-path>` and `<core-path>`

## Workflow

### Step 1: Load Specs

Read each file in `<SPEC-DOCS>` and extract:

**Tokens:**
- Colors (hex values, named variables)
- Typography (font families, sizes, weights)
- Spacing scale (values)
- Border radius values
- Shadow definitions
- Motion timings (durations, easings)
- Component-specific rules (button heights, card padding)

**Principles:**
- Stated rules from `<principles>` (e.g., forbidden visual elements, required tone, no emojis)
- Component hierarchy rules
- Responsive breakpoints

**Mechanics / Logic Rules** (if your project has them):
- Numeric constants, formulas, caps
- Structural rules (tier counts, slot counts)
- Threshold values
- Triggers and event rules

### Step 2: Scan Implementation

**For tokens mode:**

Grep `<src-path>/**/*.tsx`, `**/*.ts`, `**/*.css`, plus any framework config files for:
- Hardcoded hex colors
- Hardcoded font sizes / families
- Hardcoded px / rem values for spacing
- Hardcoded border-radius values

Build a usage inventory: which components use which values.

**For mechanics mode:**

Read the relevant modules in `<core-path>` and extract all constants, formulas, and structural definitions called out in the spec.

### Step 3: Compare

**For tokens:**

For each documented token, check:
- Does the documented value appear in code?
- Do components use the documented value, or a different one?
- Are there hardcoded values that should be using the token?

Classify findings:
- **MATCH**: code value matches spec
- **DRIFT**: code value differs from spec (document the difference)
- **UNUSED**: spec defines a token that nothing uses
- **UNDOCUMENTED**: code uses a value/pattern not in the spec

**For mechanics:**

For each documented rule, check:
- Does the code implement it?
- Do the constants match?

Classify the same way (MATCH, DRIFT, UNUSED, UNDOCUMENTED).

### Step 4: Check Stated Principles

For each principle in `<principles>`, grep the codebase for violations. Examples:
- Forbidden words or visual elements should not appear
- Em dashes (`--`) in user-facing strings, if your style rules forbid them
- Emoji in copy strings, if forbidden

### Step 5: Report

```markdown
# Spec Audit: [date]

## Summary
- Scope: [tokens | mechanics | all]
- MATCH: [N] items
- DRIFT: [N] items
- UNUSED: [N] items
- UNDOCUMENTED: [N] items
- Principle violations: [N]

## Token Drift
| Token | Spec Value | Code Value | Location | Severity |
|-------|-----------|-----------|----------|----------|
| primary-accent | #00E5FF | #00D9F0 | Button.tsx:42 | low |
| brand-gold | #FFD700 | various (hardcoded) | 5 files | medium |
...

## Mechanic / Rule Drift
| Rule | Spec | Code | Location |
|------|------|------|----------|
| Daily limit | 75-150 | 50-150 | limits.ts |
...

## Undocumented Code Patterns
[values or rules in code not mentioned in specs]

## Principle Violations
[e.g., "forbidden token found in Overlay.tsx:78"]

## Recommendations
1. [specific action, e.g., "Update Button.tsx to use primary-accent token"]
2. [...]

## Trivial Auto-Fixable (if --fix-easy mode)
- [color hex updates]
- [token reference replacements]
```

### Step 6: Follow-Up

- If `--fix-easy` mode: offer to make the trivial fixes (with user confirmation per file)
- For visual-only checks (screenshots vs spec), recommend a separate visual audit skill if available
- For subjective polish (not drift), recommend a polish skill if available
- Flag any drift that suggests the SPEC is out of date (not the code)

## Principles

- **Spec is the intended truth.** Code drift suggests either spec updates did not propagate, or code updates did not update the spec. Either way: reconcile.
- **UNDOCUMENTED is a smell, not an error.** Sometimes code legitimately runs ahead of docs; the fix is to update the spec, not the code.
- **Severity matters.** A one-pixel spacing drift is low; a color used in 20 places but not in the spec is medium; a logic rule that diverges is high.
- **Textual, not visual.** This skill compares spec text to code text. Visual compliance (do screenshots match the spec) is a separate audit.

## Anti-Patterns

- Do not auto-fix mechanic / logic drift. That is a design decision, not a token substitution.
- Do not report hundreds of low-severity findings without ranking. Fatigue kills action.
- Do not treat the spec as always correct. Flag when code suggests the spec needs updating.
- Do not duplicate visual audit work; call it as a follow-up if needed.
