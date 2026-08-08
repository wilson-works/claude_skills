# Installing agent-org in a new project

Three concrete artifacts get installed:

1. **The 70 agent `.md` files** -> `<repo>/.claude/agents/`
   - 18 CTO-branch (code-shipping, with Edit/Write)
   - 14 CFO-branch (advisory, no Edit/Write)
   - 5 COO-branch (advisory, no Edit/Write)
   - 7 CAO-branch (Chief Awareness Officer / AI oversight — Camille + Cole have Edit/Write; rest advisory)
   - 8 EA-rep-branch (Enrolled Agent / IRS representation — advisory)
   - 8 CPA-attest-branch (Audit / Attest / Assurance — advisory)
   - 10 CMO-branch (Marketing — Rocco + Tate + Yara + Luca have Edit/Write on marketing-owned paths; rest advisory)
2. **The comms CLI + db** -> `<repo>/.claude/comms/comms.py`, db auto-created at `<repo>/.claude/comms.db` on first use
3. **The path-guard hook** -> `<repo>/.claude/hooks/path_guard.py` + a `PreToolUse` registration in `<repo>/.claude/settings.json`
4. **Per-project config** -> `<repo>/.claude/agents/org.config.json`

## Step 1 - copy files

From the skills repo into your project:

```bash
SKILL_SRC=path/to/internal_claude_skills/skills/agent-org
REPO=$(git rev-parse --show-toplevel)

mkdir -p "$REPO/.claude/agents" "$REPO/.claude/comms" "$REPO/.claude/hooks"

cp "$SKILL_SRC"/agents/*.md       "$REPO/.claude/agents/"
cp "$SKILL_SRC"/comms/comms.py    "$REPO/.claude/comms/"
cp "$SKILL_SRC"/comms/schema.sql  "$REPO/.claude/comms/"
cp "$SKILL_SRC"/hooks/path_guard.py "$REPO/.claude/hooks/"
cp "$SKILL_SRC"/org.config.example.json "$REPO/.claude/agents/org.config.json"
```

PowerShell equivalent:

```powershell
$SkillSrc = "path\to\internal_claude_skills\skills\agent-org"
$Repo = (git rev-parse --show-toplevel)

New-Item -ItemType Directory -Force -Path "$Repo\.claude\agents", "$Repo\.claude\comms", "$Repo\.claude\hooks" | Out-Null
Copy-Item "$SkillSrc\agents\*.md"          "$Repo\.claude\agents\"
Copy-Item "$SkillSrc\comms\comms.py"       "$Repo\.claude\comms\"
Copy-Item "$SkillSrc\comms\schema.sql"     "$Repo\.claude\comms\"
Copy-Item "$SkillSrc\hooks\path_guard.py"  "$Repo\.claude\hooks\"
Copy-Item "$SkillSrc\org.config.example.json" "$Repo\.claude\agents\org.config.json"
```

### Want only the CTO branch?
The other 6 branches are pure-advisory (or, for CAO Copy/Coding + CMO Demand/Content, write-scoped to their own globs) and only kick in when something asks for them. They cost nothing if unused. But if you want a leaner install for a non-firm project, drop everything except CTO:

```bash
# Keep only the 18 CTO-branch agents
cp "$SKILL_SRC"/agents/cto-james.md           "$REPO/.claude/agents/"
cp "$SKILL_SRC"/agents/chief-engineer-john.md "$REPO/.claude/agents/"
cp "$SKILL_SRC"/agents/exec-assistant-tim.md  "$REPO/.claude/agents/"
cp "$SKILL_SRC"/agents/head-backend-*.md      "$REPO/.claude/agents/"
cp "$SKILL_SRC"/agents/head-frontend-*.md     "$REPO/.claude/agents/"
cp "$SKILL_SRC"/agents/head-database-*.md     "$REPO/.claude/agents/"
cp "$SKILL_SRC"/agents/head-qa-*.md           "$REPO/.claude/agents/"
cp "$SKILL_SRC"/agents/head-api-*.md          "$REPO/.claude/agents/"
cp "$SKILL_SRC"/agents/junior-*.md            "$REPO/.claude/agents/"
# (skip cfo-*, coo-*, cao-*, vp-ai-*, head-claude-*, head-copy-*, head-coding-cole.md,
#  wellness-officer-*, dor-*, head-exams-*, head-collections-*, head-notices-*,
#  cap-*, head-audit-*, head-attest-*, head-quality-*, cmo-*, head-brand-*,
#  head-demand-*, head-content-*, head-analytics-*, senior-*)
```

The comms.py knows about all 70 agents — agents you don't install simply never get spawned. The ACL still works.

### Common subset installs

- **CTO + CFO + COO** (the previous 37-agent default for firms running their own books): drop the `cao-*`, `vp-ai-*`, `head-claude-*`, `head-copy-*`, `head-coding-cole.md`, `wellness-officer-*`, `dor-*`, `head-exams-*`, `head-collections-*`, `head-notices-*`, `cap-*`, `head-audit-*`, `head-attest-*`, `head-quality-*`, `cmo-*`, `head-brand-*`, `head-demand-*`, `head-content-*`, `head-analytics-*` files.
- **CTO + CAO** (a dev shop that wants AI-oversight discipline but no finance/ops/marketing): keep CTO + CAO; skip CFO/COO/EA-rep/CPA-attest/CMO.
- **Full WilsonWorks firm-ops** (70 agents): copy all.

## Step 2 - edit org.config.json

Open `<repo>/.claude/agents/org.config.json`. The roster is fixed. Only edit:

- **`departments.<dept>.owns`** — globs for the CTO-branch path_guard. Common patterns:

| Department | Typical globs |
|------------|---------------|
| backend    | `src/server/**`, `src/services/**`, `internal/**`, `apps/api/**` |
| frontend   | `src/client/**`, `apps/web/**`, `*.css`, `*.scss` |
| database   | `migrations/**`, `**/schema.sql`, `**/alembic/**`, `**/schema.prisma` |
| qa         | `tests/**`, `**/*.test.*`, `**/*.spec.*`, `e2e/**` |
| api        | `src/api/**`, `src/routes/**`, `openapi.yaml`, `**/schemas/**` |
| copy       | `content/**`, `copy/**`, `apps/web/src/strings/**`, `**/*.mdx` |
| coding-cao | `.claude/cao-eval/**`, `.claude/agents/cao-*.md`, `.claude/agents/head-claude-*.md`, `.claude/agents/head-copy-*.md`, `.claude/agents/head-coding-*.md`, `.claude/agents/wellness-officer-*.md`, `.claude/agents/vp-ai-*.md` |
| demand     | `marketing/campaigns/**`, `marketing/paid/**`, `marketing/lifecycle/**`, `apps/web/src/landing/**` |
| content    | `marketing/content/**`, `marketing/blog/**`, `marketing/seo/**`, `apps/web/blog/**`, `apps/web/src/seo/**` |

- **`advisory_departments.<dept>.scope`** — informational bullets describing what each CFO/COO head owns. Used by cross-branch consult routing but NOT enforced by path_guard. Edit if your firm has different scope splits (e.g. payroll lives under HR vs Treasury).

- **`shared`** — paths any agent (or main session) can edit without dept-ownership enforcement: README, CLAUDE.md, docs, the backlog folder, package manifests.

## Step 3 - register the hook

Edit `<repo>/.claude/settings.json` and add the path_guard hook to PreToolUse:

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Write|Edit|MultiEdit|NotebookEdit",
        "hooks": [
          { "type": "command", "command": "python .claude/hooks/path_guard.py" }
        ]
      }
    ]
  }
}
```

If you already have PreToolUse hooks, ADD this command to the same matcher's `hooks` array — don't replace.

The matcher must list every tool in `path_guard.py`'s `PATH_TOOLS` set. `NotebookEdit` is in that set; a matcher that omits it means notebook writes never reach the guard at all.

The path_guard only fires for CTO-branch agents (Cindy, Marcus, etc.) because the CFO + COO agents don't have Edit/Write tools in the first place. Their tool calls never reach the hook.

## Step 4 - initialize the comms db (optional, lazy by default)

The DB is created on first use. To pre-create:

```bash
python .claude/comms/comms.py init
```

Verify with:

```bash
python .claude/comms/comms.py whoami james     # CTO: c-suite
python .claude/comms/comms.py whoami marcus    # Backend Junior: dev-floor
python .claude/comms/comms.py whoami elle      # CFO: cfo-suite
python .claude/comms/comms.py whoami soph      # CFO-EA: cfo-suite, cfo-dept-heads, exec-eas
python .claude/comms/comms.py whoami jas       # COO-EA: coo-suite, coo-dept-heads, exec-eas
python .claude/comms/comms.py whoami tim       # CTO-EA: c-suite, dept-heads, exec-eas
python .claude/comms/comms.py whoami amelia    # CAO: cao-suite
python .claude/comms/comms.py whoami elena     # CAO-EA: cao-suite, cao-dept-heads, exec-eas
python .claude/comms/comms.py whoami marisol   # DOR: ea-rep-suite
python .claude/comms/comms.py whoami anika     # DOR-EA: ea-rep-suite, ea-rep-dept-heads, exec-eas
python .claude/comms/comms.py whoami everett   # CAP: cpa-suite
python .claude/comms/comms.py whoami juno      # CAP-EA: cpa-suite, cpa-dept-heads, exec-eas
python .claude/comms/comms.py whoami margot    # CMO: cmo-suite
python .claude/comms/comms.py whoami rina      # CMO-EA: cmo-suite, cmo-dept-heads, exec-eas
python .claude/comms/comms.py stats
```

## Step 5 - smoke test

```bash
# CTO posts a directive
python .claude/comms/comms.py post c-suite james --to john \
  --subject "Smoke test" "Confirming the org is wired."

# John reads it
python .claude/comms/comms.py read c-suite john --unread -v

# Junior is denied from c-suite
python .claude/comms/comms.py post c-suite marcus --to john --subject "nope" "test"
# expect: ACL DENY (exit 2)

# Cross-branch consult: Tim asks Soph on exec-eas
python .claude/comms/comms.py post exec-eas tim --to soph \
  --subject "Cross-branch test" "Confirming exec-eas is wired."

# Cindy (head, NOT on exec-eas) is denied
python .claude/comms/comms.py post exec-eas cindy --to soph --subject "nope" "test"
# expect: ACL DENY (exit 2)

# CAO branch: Amelia → Elena → Camille routing
python .claude/comms/comms.py post cao-suite amelia --to elena \
  --subject "Smoke" "Confirming cao-suite."
python .claude/comms/comms.py post cao-dept-heads elena --to camille \
  --subject "Smoke" "Confirming cao-dept-heads."

# EA-rep + CPA-attest + CMO chiefs talk through their EAs
python .claude/comms/comms.py post ea-rep-suite marisol --to anika \
  --subject "Smoke" "Confirming ea-rep-suite."
python .claude/comms/comms.py post cpa-suite everett --to juno \
  --subject "Smoke" "Confirming cpa-suite."
python .claude/comms/comms.py post cmo-suite margot --to rina \
  --subject "Smoke" "Confirming cmo-suite."

# All 7 EAs now on exec-eas - Anika asks Soph for a cfo-tax consult
python .claude/comms/comms.py post exec-eas anika --to soph \
  --subject "Cross-branch test" "EA-rep consult routing to cfo-tax."
# expect: posted (exit 0)
```

### Concurrency smoke test — two claimants, one path, exactly one winner

The claim ledger is what stops two agents editing the same file. Prove it is
atomic on your machine, not just in the docs. Run against a throwaway DB.

```bash
# throwaway DB so a failed race never pollutes the real ledger
export AGENT_ORG_DB=/tmp/comms-racetest.db
rm -f "$AGENT_ORG_DB" "$AGENT_ORG_DB"-wal "$AGENT_ORG_DB"-shm
python .claude/comms/comms.py init

# two SEPARATE processes go for the same path at the same moment
python .claude/comms/comms.py claim src/contested.py cindy --wo RACE > /tmp/a.txt 2>&1 &
python .claude/comms/comms.py claim src/contested.py gavin --wo RACE > /tmp/b.txt 2>&1 &
wait
cat /tmp/a.txt /tmp/b.txt

# the ledger is the verdict: exactly one active claim on that path
python .claude/comms/comms.py claims --active
```

Expected: one process prints `claim #N active for ...`, the other prints
`CLAIM CONFLICT` or `CLAIM DENIED ... already held by ...` and exits 3.
`claims --active` must list **exactly one** row for `src/contested.py`.

Two active rows on one path is a FAILURE — it means the `BEGIN IMMEDIATE`
transaction or the `idx_claims_one_active_per_path` unique index did not take.
Check for `WARNING - could not create idx_claims_one_active_per_path` on stderr,
which means a pre-existing duplicate blocked the index at migration time.

Unset `AGENT_ORG_DB` when you are done.

If all of the above fire correctly, the org is ready.

## Step 6 - first real run

From the main session:

> "Use the cto-james agent. Direction: process work order BUG-001 from the backlog."

James will route through Tim to the right department head. Watch the comms log if you want to see the chatter:

```bash
python .claude/comms/comms.py read c-suite james --limit 50
python .claude/comms/comms.py read dept-heads tim --limit 50
python .claude/comms/comms.py read dev-floor cindy --limit 50
```

For a finance run:

> "Use the cfo-eleanor agent. Direction: get me a runway re-read with a 5-day Stripe payout slowdown baked in."

For an ops run:

> "Use the coo-mara agent. Direction: revise Roz's onboarding plan to gate first-client-data access on §7216 + WISP training completion."

For a CAO run:

> "Use the cao-amelia agent. Direction: sweep the apps/web error strings for AI-shaped writing. Route findings to Camille via Elena."

For a representation run:

> "Use the dor-marisol agent. Direction: triage the new CP2000 from Acme Inc. — coordinate with Anya on the cfo-tax preparation file via the ea-cfo-tax bridge."

For an attest run:

> "Use the cap-everett agent. Direction: kick off engagement-acceptance for the FY26 review of NewCo. Saira owns the independence wall check; Juno gates the cross-branch consult with Hal."

For a marketing run:

> "Use the cmo-margot agent. Direction: re-segment our ICP based on Q2 customer-research synthesis. Sela leads positioning revisit; Arlo redraws the funnel against the new segments."

## Maintenance

- **Archive old messages:** `python .claude/comms/comms.py archive --before 2026-01-01`
- **Inspect with sqlite:** `sqlite3 .claude/comms.db ".tables"`
- **Reset:** delete `.claude/comms.db` — auto-recreated on next use.
- **Disable enforcement temporarily:** `AGENT_ORG_DISABLE=1` env var bypasses the path guard.

## Known limitations

- Path guard relies on CTO-branch agents claiming before editing. If an agent forgets to claim, the guard cannot enforce dept ownership (it allows by default to avoid false positives in main-session work). The agent system prompts make claims a hard rule, but human-spawned agents can still skip them.
- **Concurrency envelope — read this before running lanes in separate terminals.** This bus is designed for **parallel subagents inside ONE Claude session**: one process tree, one `comms.db` writer at a time in practice. Within that envelope, two subagents racing for the same path both go through `claim`, the loser is denied at claim time (exit 3), and they coordinate on `dev-floor` rather than retrying blind.

  **Cross-terminal use — several separately-launched `claude` processes sharing one repo and one `comms.db` — is OUT OF ENVELOPE until the concurrency fixes below are calibrated.** What is now in place: `busy_timeout` on both the CLI and the hook connection, a `BEGIN IMMEDIATE` transaction plus a partial unique index (`claims(path) WHERE status='active'`) making `claim` genuinely atomic, and `path_guard.py` no longer reporting a lock error as "no claims held". What is NOT yet in place: `path_guard.py` still runs **observe-only** on unreadable claim state — it prints `*** CLAIM STATE UNREADABLE ***` and allows the write. Until `STRICT_ON_UNREADABLE_CLAIMS` is flipped (calibration condition documented in `path_guard.py`), treat the path guard as an ownership *advisory* under heavy cross-terminal contention, not a hard boundary. Do not cite it as the safety guarantee for an unattended multi-terminal run.

- **Claims expire.** A claim defaults to a 30-minute lifetime (`CLAIM_TTL_MINUTES`, override with `AGENT_ORG_CLAIM_TTL_MIN` or `claim --ttl <minutes>`; `--ttl 0` never expires). `claim` and `claims` sweep expired rows to `status='expired'`. Re-running `claim` on a path you already hold renews it instead of erroring, so a long job should re-claim periodically. Claims written before this column existed have `expires_at IS NULL` and never expire.
- The roster is fixed at 70. Adding a new department or a senior requires editing `comms.py` (ACL + DEPARTMENT_OF + ROLE_OF + CHANNELS) and `path_guard.py` (DEPARTMENT_OF) in lockstep, then writing the new agent `.md` and adding it to `org.config.json`.
- CFO + COO + EA-rep + CPA-attest + the advisory CAO/CMO heads (Amelia, Victor, Clay, Wren, Margot, Sela, Arlo) are advisory by design. If you give one of them Edit/Write tools, path_guard does not know about their department mapping and will treat them as main-session work (allow-by-default). Don't do this — keep the advisory branches advisory.
- The write-capable non-CTO depts are `copy` (Camille), `coding-cao` (Cole), `demand` (Rocco + Tate), and `content` (Yara + Luca). They are path-guard-enforced under `departments` in `org.config.json`, not `advisory_departments`.
