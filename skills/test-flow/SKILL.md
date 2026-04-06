---
name: test-flow
description: "Walks through a user flow in the browser via Chrome DevTools MCP — filling forms, clicking buttons, and verifying each step with screenshots. Supports --vertical for terminology checks and --friction for friction overlay analysis. Invoke with /test-flow [description]."
---

# Test Flow via Chrome DevTools MCP

## Purpose

Performs an interactive end-to-end walkthrough of a user flow in the browser. Fills forms, clicks buttons, navigates between pages, and screenshots each step — simulating what a real user would do.

## Prerequisites

- Chrome DevTools MCP server must be connected
- The target app must be running
- For authenticated flows: Chrome must be launched with `--remote-debugging-port=9222`

## Invocation

```
/test-flow register a new user
/test-flow complete the onboarding wizard
/test-flow claim a mission and start a session
/test-flow create a campaign as admin --vertical tax-prep
/test-flow navigate through all tabs --friction
/test-flow complete onboarding --vertical construction --friction
```

**Flags:**
- `--vertical [id]` -- Verify all UI copy uses correct vertical terminology (tax-prep, bookkeeping, legal, construction, healthcare, generic). Read `packages/core/src/verticals.ts` to load the terminology map. Flag any generic terms ("Work Items") that should be vertical-specific ("Tax Returns").
- `--friction` -- Enable friction overlay analysis at every step. In addition to the normal flow checks, evaluate each step for: missing loading feedback, unclear next actions, dead ends, poor error recovery, empty states without guidance, slow transitions (>3s), ambiguous copy, and mobile overflow issues.

## Workflow

### 1. Plan the Flow

Before touching the browser, briefly outline the steps:
- What pages will be visited
- What inputs are needed (use realistic test data)
- What the expected outcome is at each step

Present the plan to the user and proceed.

### 2. Execute Step-by-Step

For each step in the flow:

**a) Describe what you're about to do:**
> "Step 2: Filling in the workout form with: Exercise = Bench Press, Sets = 3, Reps = 10, Weight = 135 lbs"

**b) Perform the action:**
- Use `click`, `fill`, `fill_form`, `type_text`, `press_key`, `select_page` as needed
- Use `wait_for` if the page needs time to load or transition
- Use `handle_dialog` if confirmation dialogs appear

**c) Screenshot the result:**
- Take a screenshot after each meaningful step
- Note whether the result matches expectations

**d) Check for errors:**
- After each action, check `list_console_messages` for new errors
- Check `list_network_requests` for failed API calls (4xx/5xx)

### 3. Report Results

After completing the flow, provide a summary:

**Flow: [description]**

| Step | Action | Result | Status |
|---|---|---|---|
| 1 | Navigate to /dashboard | Dashboard loaded | Pass |
| 2 | Click "Log Workout" | Form opened | Pass |
| 3 | Fill form + submit | 500 error on POST | FAIL |

**Errors Found:**
- List any console errors, failed network requests, or unexpected UI states

**Screenshots:**
- Reference which screenshots correspond to which steps

### 4. Test Data Guidelines

Use realistic but clearly fake data:
- Names: "Test User", "Jane Tester"
- Email: "test@example.com"
- Numbers: realistic ranges (weight: 150 lbs, sets: 3, reps: 10)
- Dates: use today's date or reasonable recent dates
- Never use real personal data

## Vertical Mode (--vertical)

When `--vertical [id]` is provided:

1. Read `packages/core/src/verticals.ts` and load the terminology for the specified vertical
2. At every step, check all visible UI text for generic terms that should be vertical-specific:
   - "Work Item" should be the vertical's `terminology.workItem` (e.g., "Tax Return")
   - "Items" should be `terminology.workItemPlural` (e.g., "Tax Returns")
   - "Season" should be `terminology.season` (e.g., "Tax Season")
   - "Pipeline" should be `terminology.pipeline` (e.g., "Return Pipeline")
   - "Done" or "Complete" should be `terminology.complete` (e.g., "Filed")
3. Add a terminology row to the results table for any mismatches found
4. At the end, add a **Terminology Compliance** section listing all matches and mismatches

## Friction Mode (--friction)

When `--friction` is provided, add these checks at EVERY step of the flow:

| Check | What to Look For |
|-------|-----------------|
| Loading feedback | Does the page show a skeleton/spinner while data loads? Blank gaps = fail. |
| Error recovery | If something fails, is there a retry button or helpful message? |
| Empty states | Lists with no items show friendly, actionable copy (not "No data" or blank) |
| Dead ends | Can the user always proceed or go back? No trapped states. |
| Unclear CTAs | Every button/link is clearly labeled. No mystery icons. |
| Slow transitions | Any action taking >3s without feedback. Check network tab. |
| Copy clarity | Would someone new understand this page? Flag jargon without context. |
| Form validation | Inline errors on invalid input, not just post-submit. Success confirmation after submit. |
| Mobile fit | At 375px, no horizontal scrolling, no truncated critical text. |
| Navigation clarity | Active state visible, user knows where they are. |

Add a **Friction Report** section at the end:

```
### Friction Points Found
| Step | Friction Type | Description | Severity |
|------|--------------|-------------|----------|
| 3 | Missing loading state | Mission board shows blank for ~2s before data loads | Medium |
| 5 | Dead end | After completing mission, no clear next action | High |
```

## Important Notes

- This skill is for manual exploratory testing, not automated test suites
- If a step fails, note it and continue with the remaining steps if possible
- Do NOT fix bugs during the flow -- observe and report, then offer to fix after
- If the flow requires auth and you hit a login page, remind the user about the Chrome Debug shortcut
- If the user doesn't specify a flow, ask what they want to test
- When both --vertical and --friction are used together, check terminology AND friction at every step
