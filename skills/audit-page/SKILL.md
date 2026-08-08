---
name: audit-page
description: Runs a Lighthouse audit on a page via Chrome DevTools MCP, reporting scores for performance, accessibility, best practices, and SEO. Invoke with /audit-page [url].
---

# Audit Page via Chrome DevTools MCP

## Configure for your project

Before using this skill, swap this placeholder for your project value:

- `<dev-server-url>` — your dev server URL (e.g. `http://localhost:5173`)

## Purpose

Runs a full Lighthouse audit on a running web page and reports actionable findings. Use this to catch performance regressions, accessibility violations, and SEO issues.

## Prerequisites

- Chrome DevTools MCP server must be connected
- The target app must be running

## Invocation

```
/audit-page                         # Audits <dev-server-url>
/audit-page /dashboard              # Audits <dev-server-url>/dashboard
/audit-page http://localhost:3000   # Audits a specific URL
```

## Workflow

### 1. Navigate

- If a URL is provided, navigate to it
- If a path is provided (starts with `/`), prepend `<dev-server-url>`
- If nothing is provided, navigate to `<dev-server-url>`
- Wait for the page to fully load

### 2. Run Lighthouse Audit

- Use the `lighthouse_audit` tool to run a full audit
- This covers: Performance, Accessibility, Best Practices, SEO

### 3. Report Results

Provide a structured report:

**Scores:**
| Category | Score |
|---|---|
| Performance | XX/100 |
| Accessibility | XX/100 |
| Best Practices | XX/100 |
| SEO | XX/100 |

**Top Issues (by impact):**
For each category that scored below 90, list the top 3-5 issues with:
- What the issue is
- Which element(s) are affected
- How to fix it (brief, actionable)

**Quick Wins:**
Highlight any fixes that are easy to implement and have high impact.

### 4. Accessibility Deep-Dive

If the accessibility score is below 90:
- Use `take_snapshot` to get the DOM/accessibility tree
- Identify specific elements with missing ARIA labels, poor contrast, or missing alt text
- Flag any touch targets below 44x44px (recommended default, per Apple HIG's 44x44 pt guidance; WCAG 2.5.8 requires a 24x24 CSS px minimum, so treat anything under 24x24px as a hard failure)

### 5. Compare (if applicable)

If the user mentions they're checking a regression or comparing before/after:
- Note the scores and suggest re-running after fixes to compare

## Important Notes

- Lighthouse scores on localhost may differ from production (no network latency, no CDN)
- Performance scores are most useful for relative comparison (before/after), not absolute targets
- Do NOT auto-fix issues unless the user asks — this skill is observe-and-report only
- If the MCP server is not connected, tell the user and suggest restarting the session
