---
name: perf-trace
description: Records a performance trace on a page via Chrome DevTools MCP, analyzing Core Web Vitals (LCP, CLS, INP), memory usage, and runtime bottlenecks. Invoke with /perf-trace [url].
---

# Performance Trace via Chrome DevTools MCP

## Configure for your project

Before using this skill, swap this placeholder for your project value:

- `<dev-server-url>` — your dev server URL (e.g. `http://localhost:5173`)

## Purpose

Records a performance trace on a running web page, then analyzes the results to identify bottlenecks, slow renders, memory issues, and Core Web Vitals problems.

## Prerequisites

- Chrome DevTools MCP server must be connected
- The target app must be running

## Invocation

```
/perf-trace                          # Traces <dev-server-url>
/perf-trace /dashboard               # Traces <dev-server-url>/dashboard
/perf-trace /workouts after scroll   # Traces with specific interaction
```

## Workflow

### 1. Navigate

- If a URL is provided, navigate to it
- If a path is provided (starts with `/`), prepend `<dev-server-url>`
- If nothing is provided, navigate to `<dev-server-url>`
- Wait for the page to fully load

### 2. Start Trace

- Use `performance_start_trace` to begin recording
- If the user specified an interaction (e.g., "after scroll", "when opening modal"):
  - Perform that interaction using input tools (click, scroll, type_text)
- If no interaction specified:
  - Wait 3-5 seconds to capture idle performance and any lazy-loaded content
- Use `performance_stop_trace` to end recording

### 3. Analyze Trace

- Use `performance_analyze_insight` to extract metrics
- Focus on:

**Core Web Vitals:**
| Metric | Value | Rating |
|---|---|---|
| LCP (Largest Contentful Paint) | X.Xs | Good/Needs Work/Poor |
| CLS (Cumulative Layout Shift) | X.XX | Good/Needs Work/Poor |
| INP (Interaction to Next Paint) | Xms | Good/Needs Work/Poor |

Thresholds:
- LCP: Good < 2.5s, Poor > 4.0s
- CLS: Good < 0.1, Poor > 0.25
- INP: Good < 200ms, Poor > 500ms

**Long Tasks:**
- Any JavaScript tasks > 50ms blocking the main thread
- Which scripts/components are responsible

**Layout Thrashing:**
- Forced reflows or excessive layout recalculations

### 4. Memory Check

- Use `take_heapsnapshot` to capture current memory state
- Note total JS heap size
- Flag if heap seems unusually large for the page complexity

### 5. Network Context

- Use `list_network_requests` to check:
  - Total number of requests
  - Any requests > 1s
  - Any unnecessarily large payloads
  - Any requests that could be cached but aren't

### 6. Report

**Performance Summary: [page]**

| Metric | Value | Status |
|---|---|---|
| LCP | X.Xs | Good/Warn/Poor |
| CLS | X.XX | Good/Warn/Poor |
| INP | Xms | Good/Warn/Poor |
| JS Heap | XX MB | Normal/High |
| Network Requests | XX | — |
| Long Tasks | X | — |

**Top Bottlenecks:**
1. [Biggest issue] — what's causing it and how to fix
2. [Second issue] — what's causing it and how to fix
3. [Third issue] — what's causing it and how to fix

**Recommendations:**
- Prioritized list of fixes, ordered by impact
- Note which are quick wins vs larger refactors

## Important Notes

- Performance traces add overhead — numbers will be slightly worse than real usage
- Run traces multiple times if results seem inconsistent
- Most useful for before/after comparison when optimizing
- Do NOT auto-fix during the trace — report findings, then offer to fix
- localhost won't have CDN/caching benefits, so network metrics are less meaningful
- If the MCP server is not connected, tell the user and suggest restarting the session
