---
name: preflight
description: Validates that the development environment is ready for QA skills - checks dev server, Chrome DevTools MCP, and auth state. Run before other QA skills or invoked automatically by your QA runners.
---

# Preflight Environment Check

## Purpose

Lightweight health check that confirms all prerequisites are met before running browser-based QA skills. Catches silent failures early instead of letting skills produce garbage output against a broken environment.

## Configure for your project

Before using this skill, set these placeholders:

- `<dev-server-url>`: Default URL for your local dev server (e.g. `http://localhost:5173`, `http://localhost:3000`).
- `<dev-server-cmd>`: Command to start the dev server (e.g. `npm run dev` in the appropriate directory).
- `<auth-globals>` (optional): If your app exposes window globals for auth state during dev (e.g. `window.__AUTH_USER__`, `window.__TENANT_ID__`), list them here. Otherwise the skill falls back to inspecting page content.

## Invocation

```
/preflight
/preflight http://localhost:3000
```

## Workflow

### Step 1: Check Dev Server

Use `mcp__chrome-devtools__take_snapshot` to navigate to `<dev-server-url>` (or the provided URL).

- If the page loads and shows content: **PASS**
- If connection refused or timeout: **FAIL** -- tell the user to start the dev server with `<dev-server-cmd>`
- If the page shows a build/compile error overlay: **WARN** -- report the compilation error

### Step 2: Check Chrome DevTools MCP

Attempt to use `mcp__chrome-devtools__list_console_messages`.

- If it returns (even empty): **PASS**
- If the tool is not available or errors: **FAIL** -- tell the user the Chrome DevTools MCP server is not connected. They may need to restart the session or launch Chrome with `--remote-debugging-port=9222`

### Step 3: Check Auth State

Use `mcp__chrome-devtools__evaluate_script` to read any auth-state globals your app exposes during dev. Example:
```js
JSON.stringify({ authenticated: !!window.__AUTH_USER__, tenantId: window.__TENANT_ID__ || null })
```

If your app does not expose globals, check the page content instead:
- If the page shows the authenticated dashboard / main view: **PASS** (user is authenticated and has a tenant/team)
- If the page shows a login screen: **WARN** -- user is not authenticated. Skills requiring auth will fail. The agent can sign in using the project's test account credentials if available.
- If the page shows onboarding: **WARN** -- user is authenticated but has no tenant/team. Skills that test tenant features will fail.

### Step 4: Report

Output a simple status block:

```
## Preflight Check

| Check | Status | Notes |
|-------|--------|-------|
| Dev Server | PASS | <dev-server-url> responding |
| Chrome DevTools MCP | PASS | Connected |
| Auth State | PASS | Authenticated with tenant |

Ready for QA skills.
```

If any check is FAIL, stop and tell the user what to fix. If checks are WARN, report but allow the user to proceed.

## Important Notes

- This skill should take under 10 seconds
- Do NOT fix anything - only diagnose and report
- Other QA skills (e.g. `/qa-sweep`, `/validate`) should run this as their first step
- If invoked standalone, just report and exit
