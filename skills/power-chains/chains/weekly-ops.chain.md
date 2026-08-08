# chain: weekly-ops  (v1)
when-to-run: end of the work week, before planning the next one

steps:
  1. skill: /meeting-digest
     writes: the week's meeting digests        -> registry: meeting-digest
     next-step-reads: decisions, action items, and open questions from each digest
     gate: continue
  2. skill: /weekly-review
     reads: the week's digests (step 1)
     writes: weekly review with next week's Top 3   -> registry: weekly-review-file
     gate: continue
on-failure: halt chain, write partial completion report, list completed steps + artifacts
