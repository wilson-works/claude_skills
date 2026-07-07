# chain: qa-gauntlet  (v1)
when-to-run: pre-ship QA pass on a running app — verify the environment, sweep for issues, exercise flows, gate the build, and log feedback

steps:
  1. skill: /preflight
     writes: in-chat PASS/WARN/FAIL environment check (read-only; no file)  -> TODO: register
     next-step-reads: the other QA skills run preflight first and read its env status
     gate: continue
  2. skill: /qa-sweep
     reads: preflight env status (step 1)
     writes: in-chat findings report (observes only, never auto-fixes)  -> TODO: register
     gate: continue
  3. skill: /test-flow
     reads: preflight env status (step 1)
     writes: in-chat per-step flow results  -> TODO: register
     note: exercises LIVE app flows — use synthetic test data only
     gate: continue
  4. skill: /smoke-check
     reads: preflight env status (step 1)
     writes: binary PASS/FAIL verdict (includes typecheck + secrets scan + build)  -> TODO: register
     gate: continue
  5. skill: /user-feedback
     reads: findings from prior steps (steps 2-4)
     writes: findings appended to user-feedback.md REVIEW LOG  -> TODO: register
     note: promotion to backlog is user-feedback's own human-gated review step — never promote directly (built-in review gate)
     gate: continue
on-failure: halt chain, write partial completion report, list completed steps + artifacts
