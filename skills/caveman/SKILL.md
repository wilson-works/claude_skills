---
name: caveman
description: "Semantic text compression for long autonomous sessions. Strips articles, conjunctions, and filler while preserving facts, numbers, and names. Typically 40-58% token savings (observed range, varies with content type). Auto-triggers at ~50 tool call rounds or for inter-agent comms. Invoke with /caveman [on|off|compress text]."
---

# Caveman -- Semantic Context Compression

## Purpose

Reduces token usage by 40-58% (typical observed range — varies with content type) during long autonomous sessions where no human is actively reading output. Strips predictable grammar (articles, conjunctions, filler) while preserving all factual content (numbers, paths, names, code). LLMs reconstruct full meaning from compressed text with near-zero information loss.

## Invocation

```
/caveman on                    # Enable caveman mode for this session
/caveman off                   # Disable caveman mode
/caveman compress <text>       # One-shot compress a block of text
/caveman status                # Show current mode and stats
```

## Compression Rules

### STRIP (predictable, LLM reconstructs these)
1. Articles: a, an, the
2. Conjunctions: and, but, or, so, yet, for, nor
3. Logical connectors: therefore, however, furthermore, additionally, moreover, consequently
4. Filler phrases: "I think", "I believe", "it seems", "in order to", "as well as", "in terms of", "with respect to", "it is worth noting that", "it should be noted"
5. Filler words: just, really, very, quite, actually, basically, essentially, simply, literally, certainly, definitely, probably, obviously
6. Auxiliary padding: "is going to" -> "will", "in the process of" -> remove, "due to the fact that" -> "bc"
7. Passive constructions: convert to active voice

### SHORTEN (common substitutions)
| Long | Short |
|------|-------|
| because | bc |
| without | w/o |
| with | w/ |
| function | fn |
| component | comp |
| directory | dir |
| configuration | config |
| application | app |
| information | info |
| implementation | impl |
| documentation | docs |
| repository | repo |
| authentication | auth |
| development | dev |
| production | prod |
| environment | env |
| dependency | dep |
| parameter | param |

### PRESERVE (unpredictable, must keep exactly)
- File paths and URLs
- Variable names, function names, class names
- Numbers, measurements, versions
- Error messages and stack traces
- Code blocks and JSON structures
- Proper nouns and project names
- Technical terminology specific to the domain
- Command-line arguments and flags

### FORMATTING
- Limit: 2-5 words per phrase where possible
- Use `->` for causation ("leads to", "results in", "creates")
- Use `|` for list separators instead of commas in prose
- Use `:` for "has", "contains", "includes"
- Use `+` for "and" when listing items
- Newlines separate distinct thoughts (no transition words needed)

## Examples

### Status Update
```
BEFORE: "I've completed the design audit and found that the BattlePassTrack component
has a border-radius of 12px which violates the design specification of 8px. I also
noticed that the PassHeroCard component has the same issue. I'll fix both of these now."

AFTER: "Design audit done. BattlePassTrack + PassHeroCard: border-radius 12px, spec 8px. Fixing both."
```

### Technical Finding
```
BEFORE: "The application is throwing an error because the useTeam hook is being called
outside of the TeamContext provider. This is happening in the new GMPortal page component
which was added without being wrapped in the necessary context providers."

AFTER: "Error: useTeam called outside TeamContext. GMPortal.tsx missing provider wrapper. Fix: wrap in TeamContext."
```

### Milestone Log
```
BEFORE: "I have finished building all of the core components for the GM Portal feature,
including the main portal page, the members roster, and the anti-cheat monitoring panel."

AFTER: "GM Portal core done: portal page + members roster + anti-cheat panel."
```

### Inter-Agent Message
```
BEFORE: "Hey Alpha, I noticed that you modified the tokens.css file and changed the
text-secondary variable. I need to use that variable in the store components I'm building.
Can you confirm the final value so I don't have to check the file?"

AFTER: "Alpha: you changed text-secondary in tokens.css. Need final value for store comps. Confirm?"
```

## Auto-Trigger Conditions

Caveman mode activates automatically in these contexts:

### Always Caveman (regardless of mode setting)
- Background agent prompts (bg-pipeline, marathon-*, workday lane sub-agents)
- Inter-agent messages on the agent-org comms bus (`comms.py post` bodies)
- Marathon state-file notes and milestone posts to c-suite/dept-heads
- Pipeline result file entries (bg-pipeline outputs)

### Auto-Activate After Threshold
- After ~50 tool call rounds in a session (proxy for ~60% context utilization)
- When the session is running autonomously (no human messages in last 30 minutes)
- When spawned as a background agent (always starts in caveman mode)

### How to Detect Threshold
There is no direct API to measure context usage. Use these proxies:
- Count tool calls made so far in the session. After 50, activate.
- If you notice the system compressing prior messages, you're past 80% -- too late for prevention but still valuable to reduce new output.
- When in doubt, go caveman. The information loss is near-zero.

### What Changes in Caveman Mode
- All non-code text output uses compression rules
- Status messages, summaries, and explanations are compressed
- Code blocks, file edits, and JSON structures remain uncompressed
- Tool call descriptions remain clear (they're short already)
- User-facing questions remain in natural language (human readability matters)

## Manual Compression (`/caveman compress`)

```
/caveman compress "The application is currently experiencing performance issues
because the dashboard component is re-rendering on every state change, which causes
the entire component tree to update unnecessarily."
```

Output:
```
App perf issues. Dashboard re-renders every state change -> full tree update. Unnecessary.
```

## Status (`/caveman status`)

Print:
```
CAVEMAN MODE: ON (auto-triggered at tool call 52)
Session tool calls: 67
Estimated savings: ~45% token reduction on non-code output
```

Or:
```
CAVEMAN MODE: OFF
Session tool calls: 12
Auto-trigger at: ~50 tool calls
```

## Integration with the rest of the pack

The long-running skills in this pack lean on caveman compression in several places:
- **bg-pipeline** — background agent preambles and pipeline result entries use caveman format
- **agent-org comms** — `comms.py` bodies are capped at 2000 chars; caveman-compressed posts fit 2-3× more signal under the cap
- **marathon-* / workday** — state-file notes, milestone posts, and wave summaries compress; the orchestrator activates caveman once past the tool-call threshold
- **workday-watch** — `[WATCH][LANE-X]` steering posts are caveman by convention (they're read by lanes, not humans)

When those skills are active, caveman activation is handled by their own loops. You only need `/caveman on` to force it early or `/caveman off` to override the auto-trigger.

Note: Sonnet 5 and Opus 4.8 both carry 1M-token context windows, which softens the *hard* ceiling — but compression still pays: you are billed for every token you carry, and auto-compaction near ~967K is lossy. Cheap tokens are still tokens.

## Important Notes

- Caveman compression is for OUTPUT only. It does not affect how you read or process input.
- Code quality is never compromised. All code, edits, and technical implementations remain full-fidelity.
- When a human sends a direct message (not via inbox), respond in natural language regardless of caveman mode.
- The 40-58% figure is a typical observed range, not a benchmark — actual savings vary with content type. Prose-heavy output (status updates, explanations) sits near the top of the range; code-heavy output sits near the bottom, because code, paths, and identifiers are preserved verbatim and only the surrounding prose compresses.
