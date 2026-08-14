---
name: smoke-check
description: "Fast post-implementation sanity check. Runs build, secrets scan, and a minimal browser hit on key pages. Binary PASS/FAIL in about 2 minutes. Lighter than a full QA sweep. Invoke with /smoke-check [--ui|--build-only]."
---

# Smoke Check Skill

## Purpose

A full QA audit can take 15+ minutes. After a small implementation or autonomous run phase, you need a fast "did we break anything obvious?" check. This skill runs build, secrets check, and hits a few key pages in the browser to confirm the app still loads without runtime errors. Binary PASS/FAIL, no detailed reports.

## Configure for your project

Before first use, replace the following placeholders:

- `<project-root>` — absolute path to your project
- `<typecheck-cmd>` — your typecheck command (e.g. `npm run typecheck`, `npx tsc --noEmit`, `pnpm typecheck`); leave blank if not applicable
- `<secrets-scan-cmd>` — your secrets/env-leak guard command (e.g. `npm run check:secrets`, `gitleaks detect`); leave blank if not applicable
- `<build-cmd>` — your production build command (e.g. `npm run build`)
- `<dev-server-url>` — local dev server URL (e.g. `http://localhost:5173`, `http://localhost:3000`)
- `<smoke-pages>` — list of 3 key routes to hit (e.g. `/`, `/dashboard`, `/settings`); pick the most-traversed pages
- `<full-qa-skill>` — the slash command for your full QA audit (e.g. `/qa-sweep`)
- `<ui-review-skill>` — the slash command for deeper UI inspection (e.g. `/review-ui`)

## Invocation

```
/smoke-check                - full smoke: build + secrets + 3 key pages
/smoke-check --build-only   - skip the browser, just build + secrets + typecheck
/smoke-check --ui           - browser-only (assumes build already passed)
```

## Prerequisites

- **Always**: ability to run shell commands in `<project-root>`
- **For --ui or default**: dev server running at `<dev-server-url>`, browser automation MCP (e.g. Chrome DevTools MCP) connected

## Workflow

### Step 1: Preflight

Quick environment check:
- Confirm `<project-root>` exists and is the current project
- Check if dev server is up at `<dev-server-url>` (only needed for --ui or default)
- If dev server missing and not in --build-only mode, ask the user to start it or fall back to --build-only

### Step 2: Build + Static Checks

Run in sequence, stopping on first failure:

1. **Typecheck**: `<typecheck-cmd>` — must pass (skip if blank)
2. **Secrets scan**: `<secrets-scan-cmd>` — must pass (skip if blank)
3. **Build**: `<build-cmd>` — must complete without errors

If any step fails, capture the error, report FAIL, stop.

### Step 3: Browser Smoke (skip if --build-only)

Use the browser automation MCP to:

For each route in `<smoke-pages>`:
1. Navigate to `<dev-server-url><route>`
2. Wait for initial render
3. Capture any `console.error` messages
4. Check for blank-page / error-boundary state

No screenshots, no detailed DOM inspection — this is a smoke check, not a UI audit.

### Step 4: Verdict

**PASS** if:
- All build steps succeeded
- No console errors on the smoke pages
- No blank/error screens

**FAIL** if:
- Any build step failed
- Any console error on a smoke page
- Any blank screen or error boundary triggered

### Step 5: Report

One-block output:

```
Smoke check: PASS (1:47)
- Typecheck: OK
- Secrets: OK
- Build: OK (4.2s)
- /: loaded, 0 console errors
- /dashboard: loaded, 0 console errors
- /settings: loaded, 0 console errors
```

Or on failure:

```
Smoke check: FAIL (0:31)
- Typecheck: FAIL
  Error: Type 'undefined' is not assignable to 'string'
    <src-path>/MyComponent.tsx:42
- Stopped before other steps.
```

### Step 6: Follow-Up Hints

- If PASS: suggest `<full-qa-skill>` for full audit if this was pre-deploy
- If FAIL on typecheck: show the first error location for quick fix
- If FAIL on runtime: suggest `<ui-review-skill>` on the failing page for deeper diagnosis

## Principles

- **Fast over thorough.** Target under 2 minutes. If we find ourselves expanding the check, that's full-QA territory.
- **Binary verdict.** No "PASS WITH WARNINGS". Either it smokes clean or it doesn't.
- **Stop on first failure.** No reason to run the browser check if typecheck failed.
- **Three pages is enough.** Pick the most-traversed routes and stick to them. Don't expand without reason.

## Anti-Patterns

- Do not run this INSTEAD of full QA before a production deploy. This is a post-phase sanity check, not a release gate.
- Do not produce a detailed report; that's the full QA skill's job.
- Do not capture screenshots; they slow the skill down and add no value at this level.
- Do not suggest fixes in the report beyond pointing at the first error; a human should decide the fix.
