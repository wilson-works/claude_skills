# chain: launch-day  (v1)
when-to-run: shipping a launchable release and the launch date is set

steps:
  1. skill: /product-marketing-context
     writes: .agents/product-marketing-context.md (12-section context doc)  -> registry: product-marketing-context
     next-step-reads: other marketing skills read this doc automatically; launch-strategy pulls positioning + ICP sections
     gate: continue
  2. skill: /launch-strategy
     reads: product-marketing-context (step 1)
     writes: launch plan (channel list, timeline, messaging) — produced IN-CONVERSATION with no file of its own; this step MUST save the plan to a file so later steps can read it  -> TODO: register (launch plan has no registry entry)
     next-step-reads: channel list + launch timeline
     gate: continue
  3. skill: /directory-submissions
     reads: launch plan channel list (step 2)
     writes: directory plan + submission tracker CSV  -> TODO: register
     gate: STOP  -- the actual submissions to external directories are outward-facing; drafting the plan/tracker may proceed, submitting may not; resume only on explicit user go
  4. skill: /social-content
     reads: product-marketing-context (step 1) + launch plan (step 2)
     writes: launch posts + content calendar (DRAFTS only)  -> TODO: register
     gate: STOP  -- publishing is outward-facing and a user action; drafts may proceed, posting may not
  5. skill: /analytics-tracking
     reads: launch plan channel list (step 2)
     writes: tracking plan with UTM strategy (UTMs per channel)  -> TODO: register
     gate: continue
on-failure: halt chain, write partial completion report, list completed steps + artifacts
