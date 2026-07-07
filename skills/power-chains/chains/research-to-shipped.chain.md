# chain: research-to-shipped  (v1)
when-to-run: turning a research queue into shipped work — from cited reports through council-approved work orders to code and a retro

steps:
  1. skill: /marathon-research
     writes: cited report folders under <research-root>  -> registry: research-report
     next-step-reads: marathon-research auto-fires /distill on completion (Phase 4)
     gate: continue
  2. skill: /distill
     reads: research-report (step 1)
     writes: <=200-line summary cards at research/summaries/ (Action Items consumable by /backlog)  -> registry: distilled-card
     gate: continue
  3. skill: /council-rd
     reads: distilled-card + research reports (steps 1-2)
     writes: top 2-3 work orders filed to backlog category files; emits an HTML approve/review/disapprove tool  -> registry: backlog-item
     gate: detour: council-rd's own HTML approval (BUILT-IN DETOUR — approve/review/disapprove each WO; reconcile deletes DISAPPROVED items), then return
  4. skill: /backlog
     reads: filed work orders (step 3)
     writes: backlog items with routing fields  -> registry: backlog-item
     gate: continue
  5. skill: /work-orders
     reads: backlog-item (step 4)
     writes: code in isolated worktree branches work-orders/[ID]  -> TODO: register
     note: spawns agents that WRITE CODE but does NOT commit or merge. DISCREPANCY: the power-chains SKILL.md canonical table says "writes + commits"; verification shows it does NOT commit. This chain reflects verified reality — no commit, no merge.
     gate: STOP  -- the merge decision is the user's; the user decides which branches merge
  6. skill: /retro
     reads: this chain's completion report (retro evidence)
     writes: retro doc to <retros-path>  -> TODO: register
     gate: continue
on-failure: halt chain, write partial completion report, list completed steps + artifacts
