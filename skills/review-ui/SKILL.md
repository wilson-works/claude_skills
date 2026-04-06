---
name: review-ui
description: Uses Chrome DevTools MCP to take screenshots, inspect DOM, check console errors, and test responsive layouts on a running web app. Invoke with /review-ui [url] or /review-ui [url] [description of what to check].
---

# Review UI via Chrome DevTools MCP

## Purpose

This skill uses the Chrome DevTools MCP server to visually review a running web application. It navigates to the specified URL, takes screenshots, checks for errors, and reports findings — closing the gap between code changes and visual verification.

## Prerequisites

- Chrome DevTools MCP server must be connected (configured in `.mcp.json`)
- The target app must be running (e.g., `localhost:5173` for Vite dev server)
- For authenticated pages: Chrome must be launched with `--remote-debugging-port=9222` and the MCP config must include `--browserUrl=http://127.0.0.1:9222`

## Invocation

```
/review-ui                          # Reviews localhost:5173 (default)
/review-ui http://localhost:3000    # Reviews a specific URL
/review-ui /dashboard               # Reviews localhost:5173/dashboard
/review-ui /settings check mobile   # Reviews with specific instructions
```

## Workflow

### 1. Navigate

- If a URL is provided, navigate to it
- If a path is provided (starts with `/`), prepend `http://localhost:5173`
- If nothing is provided, navigate to `http://localhost:5173`
- Wait for the page to fully load

### 2. Desktop Screenshot + Console Check

- Take a screenshot at the current viewport size
- Read console logs and check for errors or warnings
- Check for failed network requests

### 3. Mobile Screenshot

- Resize viewport to 375px width (standard mobile breakpoint)
- Take a second screenshot
- Note any layout issues (overflow, truncation, touch target sizing)

### 4. Report Findings

Provide a structured report:

**Visual Check:**
- What the page looks like at desktop and mobile sizes
- Any obvious layout, styling, or rendering issues

**Console:**
- Any JavaScript errors or warnings
- Any failed network requests

**Accessibility:**
- Note any obvious issues (missing alt text, contrast, touch targets < 44x44px)

**Recommendations:**
- Only flag actual problems — do not invent issues
- If everything looks good, say so

### 5. If User Provided Specific Instructions

Focus the review on whatever the user asked about (e.g., "check if the modal opens", "verify the chart renders", "test the form submission flow"). Use click, fill, type_text, and other input tools as needed.

## Important Notes

- Do NOT make code changes during this skill — only observe and report
- If the MCP server is not connected, tell the user and suggest they check their `.mcp.json` config and restart the session
- If the page requires auth and shows a login screen, tell the user to relaunch Chrome with `--remote-debugging-port=9222`
