# The Agent Org — How the Team Works Together

A friendly map of the **18-agent CTO organization** that ships in `agent-org` (and that
`marathon-org`, `work-orders-org`, and `workday` drive). It's a small software company that
happens to be made of agents: a C-suite that sets direction, an exec assistant who routes,
department heads who review, and juniors who write the code — all talking over a hard-ACL
comms bus.

> Diagrams render automatically on GitHub. For a one-page shareable version, open
> [`org-poster.html`](org-poster.html) in a browser.

---

## 1. Chain of command

The CEO (you) sets intent. James turns it into technical direction. Tim routes work to the
right department. Heads own quality in their area. Juniors implement. John is the
independent merge gate — he answers to no department, so nothing lands on his say-so alone.

```mermaid
flowchart TD
  CEO([CEO · you]):::ceo

  CEO --> James[James · CTO<br/>strategy & go/no-go]:::csuite
  James --> John[John · Chief Engineer<br/>architecture · final review]:::gate
  James --> Tim[Tim · Exec Assistant<br/>the routing funnel]:::csuite

  Tim --> Cindy[Cindy · Backend Head]:::head
  Tim --> Gavin[Gavin · Frontend Head]:::head
  Tim --> Diana[Diana · Database Head]:::head
  Tim --> Rachel[Rachel · QA Head]:::head
  Tim --> Josh[Josh · API Head]:::head

  Cindy --> CB["Marcus · Priya<br/>(backend juniors)"]:::jr
  Gavin --> GB["Ava · Kai<br/>(frontend juniors)"]:::jr
  Diana --> DB["Leo · Nora<br/>(database juniors)"]:::jr
  Rachel --> RB["Owen · Maya<br/>(QA juniors)"]:::jr
  Josh --> JB["Felix · Zara<br/>(API juniors)"]:::jr

  CB -.diff.-> John
  GB -.diff.-> John
  DB -.diff.-> John
  RB -.diff.-> John
  JB -.diff.-> John
  John -.approve / bounce.-> CEO

  classDef ceo fill:#1f6feb,stroke:#58a6ff,color:#fff,font-weight:bold
  classDef csuite fill:#161b22,stroke:#58a6ff,color:#e6edf3
  classDef gate fill:#3d1d00,stroke:#e3b341,color:#ffdf5d,font-weight:bold
  classDef head fill:#161b22,stroke:#2dd4bf,color:#e6edf3
  classDef jr fill:#0d1117,stroke:#8b949e,color:#c9d1d9
```

**Read it as:** authority flows **down** (CEO → James → Tim → head → junior). Finished work
flows **up through John** — the review gate is deliberately *off* the command line so a head
can't approve their own team's slop.

---

## 2. The comms bus & the hard ACL

Every tier has its own SQLite-backed channel. The walls are **enforced, not polite**: a
junior literally cannot post to the CTO. Cross-tier messages go through the person whose job
is to bridge that gap (Tim, mostly). A path-guard hook blocks any agent from editing files
outside its department's territory.

```mermaid
flowchart LR
  subgraph c["#quot;c-suite#quot; channel"]
    direction TB
    A1[James]:::csuite
    A2[John]:::gate
    A3[Tim]:::csuite
    A4([ceo — reserved label<br/>for posts to the human]):::ceo
  end

  subgraph d["#quot;dept-heads#quot; channel"]
    direction TB
    B0[Tim]:::csuite
    B1[Cindy]:::head
    B2[Gavin]:::head
    B3[Diana]:::head
    B4[Rachel]:::head
    B5[Josh]:::head
  end

  subgraph f["#quot;dev-floor#quot; channel"]
    direction TB
    C0[Heads]:::head
    C1[Juniors ×10]:::jr
  end

  c <-->|Tim is the only<br/>member of both| d
  d <-->|heads bridge<br/>down to the floor| f
  f x--x|HARD ACL: a junior<br/>cannot reach the CTO| c

  PG{{path-guard hook<br/>blocks out-of-territory<br/>Edit / Write}}:::gate
  f -.every edit checked.-> PG

  classDef ceo fill:#1f6feb,stroke:#58a6ff,color:#fff
  classDef csuite fill:#161b22,stroke:#58a6ff,color:#e6edf3
  classDef gate fill:#3d1d00,stroke:#e3b341,color:#ffdf5d
  classDef head fill:#161b22,stroke:#2dd4bf,color:#e6edf3
  classDef jr fill:#0d1117,stroke:#8b949e,color:#c9d1d9
```

| Channel | Who's on it | Purpose |
|---|---|---|
| `c-suite` | James, John, Tim (+ `ceo` label for you) | direction, go/no-go, final summaries |
| `dept-heads` | Tim + the 5 heads | routing, pre-review digests |
| `dev-floor` | heads + the 10 juniors | claims, implementation chatter, hand-offs |

Before editing a file an agent **claims** it (`comms.py claim <path> <agent> --wo <id>`), so
two agents never silently fight over the same file.

---

## 3. How a work order actually runs (the loop)

The nominal chain is CEO → James → Tim → head → junior → head → Tim → **John gate** → merge.
But here is the part most people miss:

> **Execution model:** in this Claude Code environment a sub-agent **cannot spawn another
> sub-agent**. So the top-level session (the orchestrator) does *all* the spawning. The
> chain above is the **accountability model**, not a literal call stack. The orchestrator
> spawns the head to implement and John to review; James/Tim give advisory direction. The
> review gates and named ownership survive — only the spawn-theater is dropped.

```mermaid
sequenceDiagram
  autonumber
  participant CEO as CEO
  participant J as James (CTO)
  participant T as Tim (EA)
  participant H as Dept Head
  participant Jr as Junior (implements)
  participant John as John (merge gate)

  CEO->>J: work order (intent)
  J->>T: priority + accountability
  T->>H: route to the right dept
  H->>Jr: assign + directional brief
  Jr->>Jr: claim paths, implement, self-check
  Jr->>H: diff back on dev-floor
  H->>T: pre-review digest (catches slop early)
  T->>John: hand to the gate
  John-->>CEO: ✅ approve → merge & log
  John-->>H: ❌ bounce with reasons → loop back
```

It is a **loop, not a line**: a bounce from John sends the WO back to the head with concrete
reasons, and it re-enters at "implement". A WO only leaves the loop when John approves *and*
the verification suite is green.

---

## 4. The parallel loop — `/workday`

`/workday` runs four of these loops at once, each in its own git worktree so they can never
collide on a write, then merges them in dependency order. `/workday-watch` is an optional
fifth session that watches the four and nudges them back on course in real time.

```mermaid
flowchart TD
  WD[/workday plans the night/]:::csuite
  WD --> GOAL[John sets a completion<br/>GOAL per lane]:::gate

  GOAL --> LA[Lane A · schema<br/>own worktree]:::head
  GOAL --> LB[Lane B · backend<br/>own worktree]:::head
  GOAL --> LC[Lane C · frontend<br/>own worktree]:::head
  GOAL --> LD[Lane D · api<br/>own worktree]:::head

  LA --> LANELOOP{{each lane =<br/>a marathon-org loop<br/>· no idle waves<br/>· staggered safety cron}}:::jr
  LB --> LANELOOP
  LC --> LANELOOP
  LD --> LANELOOP

  LANELOOP --> LE[Lane E · auto-merge<br/>a→b→d→c · verify · clean up]:::gate
  LE --> DONE([trunk updated · run archived]):::ceo

  WW[[/workday-watch · optional<br/>C-suite surveillance]]:::watch
  WW -. reads state + comms .-> LANELOOP
  WW -. WATCH steering posts<br/>the lanes obey .-> LANELOOP

  classDef ceo fill:#1f6feb,stroke:#58a6ff,color:#fff
  classDef csuite fill:#161b22,stroke:#58a6ff,color:#e6edf3
  classDef gate fill:#3d1d00,stroke:#e3b341,color:#ffdf5d
  classDef head fill:#161b22,stroke:#2dd4bf,color:#e6edf3
  classDef jr fill:#0d1117,stroke:#8b949e,color:#c9d1d9
  classDef watch fill:#1a1633,stroke:#a371f7,color:#d2c5ff
```

**Why it's safe to leave running overnight:** disjoint worktrees + disjoint territory mean
no lane can corrupt another's work; Lane E is *always* automated so the merge never lands on
a human at 8 AM; and the safety crons are staggered so a session-limit reset doesn't wake all
four at the same instant.

---

## Cast (18 agents)

| Tier | Agents |
|---|---|
| C-suite | **James** (CTO) · **John** (Chief Engineer / merge gate) · **Tim** (Exec Assistant) |
| Heads | **Cindy** (backend) · **Gavin** (frontend) · **Diana** (database) · **Rachel** (QA) · **Josh** (API) |
| Juniors | Marcus · Priya · Ava · Kai · Leo · Nora · Owen · Maya · Felix · Zara |

C-suite + heads run on the deeper model for judgment; juniors run on the faster model for
throughput. Drop the org into any repo, point `org.config.json` at your path globs, and go.
