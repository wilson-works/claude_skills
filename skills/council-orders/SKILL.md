---
name: council-orders
description: "Convene a 5-member product council where each member contributes 5 backlog work orders, and a Chairman adds 5 synthesis items. All 25-30 work orders filed to backlog. Invoke with /council-orders [optional focus]."
---

# Council Orders Skill

## Purpose

Convene an LLM council of 5 product advisors. Each produces 5 work orders from their lens. Chairman synthesizes and adds 5 gap items. All filed to backlog.

This is the single-session variant. For multi-wave rotating sessions, use `/marathon-council`.

## Invocation

```
/council-orders                     Default: enterprise readiness framing
/council-orders [focus]             Custom framing (e.g. "security hardening", "mobile QA")
```

## Configuration (EDIT THESE)

```
BACKLOG_DIR: [your backlog directory]    # e.g., ~/.claude/projects/myproject/backlog/
PRODUCT_CONTEXT: [edit the block below for your product]
```

## The Five Council Members

1. **Enterprise Sales Engineer** -- gaps that kill demos (admin, audit, SSO, provisioning)
2. **Staff Security Engineer** -- gaps that fail compliance (auth, rules, PII, rate limiting)
3. **Principal Product Designer** -- gaps that read as "prototype" (states, typography, mobile)
4. **Staff Platform Engineer** -- gaps at scale (hot docs, cold starts, indexes, cost)
5. **L&D / HR Tech Buyer** -- gaps for buyers (reporting, accessibility, fairness, compliance)

After 5 members: **Chairman** synthesizes + adds 5 gap items.

---

## Steps

### 1 -- Read backlog state

Read four files to get `<!-- Next ID: N -->` and last 20-30 items (dedup).

### 2 -- Spawn 5 advisors in parallel

Each receives: lens, product context, backlog summary, framing.

**TOKEN OPTIMIZATION**: Use `model: "sonnet"` for advisors.

**Advisor prompt:**
```
You are [TITLE] on a product council for [APP_NAME].
Lens: [2 sentences]

[COMPACT PRODUCT CONTEXT]

FRAMING: [focus or default: "Enterprise readiness. What would kill a demo?"]

ALREADY FILED (skip these):
[last 20-30 item titles]

Produce exactly 5 work orders a developer can execute.
Format:
[CATEGORY] Title
Priority: critical/high/medium/low
Details: 2-3 sentences. Name components/files.
Why: one sentence.

No preamble. 5 items only.
```

**Lens descriptions (keep compact):**

- *Sales*: "10 years of Fortune 500 demos. VP HR, CTO, Sales Ops director objections. Admin controls, audit, SSO, HRIS export."
- *Security*: "Reviewed dozens of SaaS products. SOC 2, pen-test, compliance. Auth, Firestore rules, PII, rate limiting, idempotency."
- *Design*: "Shipped enterprise design systems. 10-second glance test. Empty/loading/error states, typography, mobile, transitions, icon consistency."
- *Platform*: "Ran infra 0 to millions of users. Hot documents, cold starts, indexes, fan-out, cost runaway, monitoring gaps."
- *HR Buyer*: "Evaluated 20+ HR tools. Manager reporting, HRIS, accessibility, fairness, opt-out rights, DPA."

### 3 -- Collect and deduplicate

Merge overlapping items from different advisors into one comprehensive item.

### 4 -- Chairman

```
You are Chairman of a product council for [APP_NAME].
5 advisors submitted 25 work orders.
1. Brief synthesis (under 150 words): convergence, divergence, most critical finding.
2. Add exactly 5 NEW work orders for gaps all advisors missed.

[25 WORK ORDER TITLES + DETAILS]

Same format as above. Output: synthesis, then 5 items.
```

### 5 -- File to backlog

Sequential IDs, priority-sorted, tagged `- **Council**: [Advisor]`.

```markdown
### [FTR-XXX] Title
- **Added**: YYYY-MM-DD
- **Priority**: critical/high/medium/low
- **Council**: [Advisor name or "Chairman synthesis"]
- **Details**: ...
- **Context**: ...
```

Update `<!-- Next ID: N -->` in each file.

### 6 -- Report

1. Chairman synthesis
2. Table of all items by advisor (ID, title, priority, category)
3. Priority breakdown
4. Top 3 urgent items

---

## Product Context Block (EDIT THIS)

```
PRODUCT: [App Name] -- [one-line description].
[2-3 sentence summary].
Tech: [stack].
Key data: [collections/models].
Pricing: [tiers].
Hard rules: [constraints].
```

## Custom Framing Examples

```
/council-orders                    Default enterprise readiness
/council-orders beta launch        What blocks a clean beta?
/council-orders security           Security-focused sweep
/council-orders mobile             Mobile experience gaps
/council-orders post-incident      What to fix after an incident
```

## Setup

1. Copy into `~/.claude/skills/council-orders/`
2. Edit Product Context Block
3. Edit advisor lenses if your domain differs
4. Create backlog files with `<!-- Next ID: 001 -->` headers
5. Run `/council-orders` to test
