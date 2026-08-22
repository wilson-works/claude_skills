---
name: qa-sweep
description: "Parameterized QA audit that walks a section of a web app, verifying functionality, checking for friction, and flagging enhancements. Replaces separate functionality, admin, and friction auditors. Invoke with /qa-sweep [section] [--checklist name]."
---

# QA Sweep Skill

## Configure for your project

Before using this skill, swap these placeholders for your project values:

- `<dev-url>` — your dev server URL (e.g. `http://localhost:5173`)
- `<src-path>` — your source root (e.g. `src/`, `apps/web/src/`)
- `<nav-config>` — path to your navigation config / route table if you keep one (e.g. `src/config/nav.ts`)
- `<design-spec>` — optional path to your design tokens / spec file (e.g. `DESIGN.md`)
- `<sections>` — list of high-level sections of your app (replace the example sections in the table below with your real ones)
- `<test-account>` — if your app requires login, use a dedicated test account; configure credentials via environment variables, not in this skill file.

If your project has domain-specific terminology you want verified across copy (e.g. role-name conventions, branded labels), define it in your project context file and reference it here. The original version of this skill used a `--vertical` flag; remove that flag or repurpose it for your own per-domain checks.

## Purpose

One skill to rule them all. Walks any section of your app through the browser, screenshots key states, verifies data renders correctly, checks console for errors, tests interactive elements, and reports findings with severity-ranked plain-language verdicts.

Replaces the need for separate Functionality Audit, Admin Settings Auditor, and Friction Auditor skills by using parameterized sections and built-in checklists.

## Invocation

```
/qa-sweep <section>
/qa-sweep all
/qa-sweep <section> --checklist <name>
```

**Arguments:**
- `[section]` — Required. One of your app's defined sections (see table below) or `all`
- `--checklist [name]` — Optional override. Uses a custom checklist focus (see Built-in Checklists below)

## Prerequisites

- Dev server running at `<dev-url>`
- Chrome DevTools MCP server connected
- For admin sections: user authenticated as owner or admin role
- For all sections: user authenticated (use the test account credentials from env vars)

## Workflow

### Step 0: Preflight

Run preflight checks before starting. If dev server or MCP fails, stop. If auth warns, note which sections will be limited.

### Step 1: Read Context

Before touching the browser, read these files for current state:

- `<nav-config>` — Navigation structure
- `<design-spec>` — Design tokens and component specs (if checking visual compliance)
- Any per-domain terminology source if your app has one

### Step 2: Navigate to Section

Map the section argument to a route. EDIT THIS table for your project:

| Section | Route | Sub-views to check |
|---------|-------|--------------------|
| home | `/` | (your sub-views) |
| onboarding | `/onboarding` | Full onboarding flow |
| admin | `/admin` | (admin sub-views) |
| ... | ... | ... |
| all | All of the above | Sequential sweep |

Navigate to the section. Take an initial desktop screenshot (1280px) and mobile screenshot (375px).

### Step 3: Run the Section Checklist

Each section has a built-in checklist. Execute every item. For each check:

1. **Perform the check** (screenshot, click, inspect, read console)
2. **Record the result** (pass, warn, fail)
3. **Note specifics** (what was expected vs what was found)

---

## Built-in Checklists (EDIT for your project)

The checklists below are example shapes. Keep the structure (one heading per section, bullet checks) and replace the specifics with what's load-bearing for your app.

### Home / Hub Checklist
- [ ] Page loads without console errors
- [ ] Primary status / progress indicator displays correctly
- [ ] Active CTAs are clickable, hover states work
- [ ] Recent activity feed loads (or shows empty state if no data)
- [ ] Mobile: all content accessible without horizontal scroll
- [ ] Mobile: touch targets at least 44px
- [ ] Loading states: skeleton or spinner before data loads (not blank white)
- [ ] Empty states: friendly message when there's no data
- [ ] No stale data: refresh and verify reload

### Primary Feature Checklist (replace with the main thing your app does)
- [ ] Feature loads with available items
- [ ] Items show all key fields (status, deadline, owner, etc.)
- [ ] Primary action button works (claim, start, complete)
- [ ] Detail view opens on click
- [ ] Completed items display completion state
- [ ] Mobile: cards stack vertically, no overflow
- [ ] Console: no errors on interactions
- [ ] Network: no failed API calls

### Progress / Profile Checklist
- [ ] Profile section displays user fields correctly
- [ ] Stat trackers display (whatever your stats are)
- [ ] Achievement / unlock state displays correctly
- [ ] Locked items shown distinctly from unlocked
- [ ] Mobile: profile sections stack cleanly
- [ ] Console: no errors loading profile

### Admin Checklist
- [ ] Admin section only visible to owner/admin roles
- [ ] Health metrics dashboard loads with real data
- [ ] CRUD forms: validation works, required fields enforced
- [ ] Member roster displays with status indicators
- [ ] Role management works (if owner)
- [ ] Plan/billing settings accessible
- [ ] Console: no errors on admin operations
- [ ] Network: CRUD operations produce 2xx responses

### Onboarding Checklist
- [ ] Landing page loads without errors
- [ ] Auth page: login and signup forms functional
- [ ] Onboarding flow: each step has a clear next action
- [ ] Form validation works inline
- [ ] First-success moment fires after completion
- [ ] Mobile: onboarding fits screen without horizontal scroll
- [ ] No dead ends: every state has a clear next action
- [ ] Back navigation works at every step

---

## Friction Overlay

In addition to the section-specific checklist, ALWAYS check these friction indicators on every page visited:

### Universal Friction Checks
- [ ] **Loading feedback**: every data-dependent section shows a loading state before content appears. Blank white gaps = friction.
- [ ] **Error recovery**: if a network request fails, user sees a retry option or helpful message. Page does not break silently.
- [ ] **Empty states**: every list/feed/collection that could be empty shows a friendly, actionable message. Not "No data" or blank.
- [ ] **Dead ends**: nowhere the user can navigate to but has no way to proceed or go back.
- [ ] **Unclear CTAs**: every button and link clearly labeled. No "Click here" or unlabeled icon buttons.
- [ ] **Slow loads**: no page or interaction takes >3 seconds without feedback.
- [ ] **Mobile overflow**: no horizontal scrolling on mobile (375px).
- [ ] **Keyboard dismiss**: check `keyboard-dismiss` (see `ui-ux-pro-max`) on every text field hit during the sweep.
- [ ] **Copy clarity**: UI copy clear to a first-time user. Flag jargon without context.
- [ ] **Form feedback**: forms show validation errors inline (not just after submit). Show success confirmation after submit.
- [ ] **Navigation clarity**: user always knows where they are. Active tab highlighted. Breadcrumbs if nested.

---

### Step 4: Screenshot Evidence

For every WARN or FAIL finding:
1. Take a screenshot showing the issue
2. If a console error, capture the error text
3. If a network failure, note the URL and status code

### Step 5: Report

Output a structured, plain-language report:

```
## QA Sweep Report — [section]

### Overall Verdict: PASS / NEEDS WORK / FAILING
[One sentence summary]

### Critical Issues (breaks functionality)
1. [Description in plain language]. Found on: [page/route]. Screenshot: [ref].
   **Fix:** [Suggested fix if obvious]

### Warnings (degrades experience)
1. [Description]. Found on: [page/route].
   **Suggestion:** [Enhancement idea]

### Friction Points
1. [Description of friction]. Where: [page/action].
   **Impact:** [What a user would feel: confused, stuck, annoyed]

### Passing Checks
- [Grouped list of things that work]

### Enhancement Ideas
- [Non-critical improvements spotted during the sweep]

### Checklist Score: X/Y passed (Z%)
```

### Step 6: Offer to Fix

After reporting, ask the user:
> "Found X issues. Want me to fix the critical and warning items? I'll leave friction points and enhancements for your review."

Only fix if the user says yes. Do NOT auto-fix during the sweep.

---

## Running `all` Sections

When invoked as `/qa-sweep all`:

1. Run each section sequentially.
2. After all sections complete, output a summary dashboard:

```
## Full QA Sweep Summary

| Section | Critical | Warnings | Friction | Score |
|---------|----------|----------|----------|-------|
| Home | 0 | 1 | 2 | 85% |
| Feature A | 1 | 0 | 1 | 70% |
| ... | ... | ... | ... | ... |
| **Total** | **3** | **5** | **7** | **79%** |

### Top 3 Priorities:
1. [Most critical finding]
2. [Second most critical]
3. [Third most critical]
```

## Integration with /loop

When invoked via `/loop 15m /qa-sweep [section]`:
- Focus on changed pages since last run (check `git status` for modified components)
- Skip sections that passed fully in the previous run
- Report only new findings

## Important Notes

- This skill OBSERVES first, REPORTS second, FIXES only on user approval.
- Plain language always. "The list shows no items even though there are 3 in the database" not "Data binding failure on ListView.tsx".
- The friction overlay runs on EVERY section, not just when explicitly requested.
- Screenshots are evidence. Take them liberally at every WARN and FAIL.
- If a section is completely broken (page crash, blank screen), note it and move on rather than getting stuck.
