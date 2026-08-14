---
name: arch-diagram
description: "Generates professional dark-themed SVG architecture diagrams from a project architecture config file (e.g. universe.json). Produces self-contained HTML files with no external dependencies. Invoke with /arch-diagram [view] [--refresh]. Views: full, frontend, backend, infra, game, data-flow, all."
---

# Architecture Diagram Skill

Generates beautiful, dark-themed SVG architecture diagrams from a project architecture config file. Produces self-contained HTML files with embedded SVG, JetBrains Mono typography, semantic color coding by component type.

## Configure for your project

Before using this skill, set these placeholders to match your project:

- `<arch-config-path>`: Absolute path to your architecture JSON config file (e.g. `d:/myproject/dev-universe/universe.json`).
  - The file must export `meta`, `nodes[]`, and `edges[]` (see Source Data section).
- `<arch-output-dir>`: Absolute directory where generated `arch-*.html` files will be written (e.g. `d:/myproject/dev-universe/`).
- `<project-name>`: Display name used in the diagram title and header (e.g. "MyApp").
- View definitions (frontend/backend/infra/game/data-flow): Edit the View Definitions section below to match your actual stack and component layout.
- Layer color mapping: The default mapping covers common layers (`user`, `frontend`, `backend`, `database`, `infra`, `external`, `game`, `security`). Adjust if your `node.layer` values differ.

## Invocation

```
/arch-diagram              Generate full system overview
/arch-diagram full         Full system - all layers, all connections
/arch-diagram frontend     Frontend layer
/arch-diagram backend      Backend layer
/arch-diagram infra        Infrastructure layer
/arch-diagram game         Domain/business-logic layer (rename for non-game projects)
/arch-diagram data-flow    Data flow: how data moves from user action to database and back
/arch-diagram all          Generate all five views
/arch-diagram --list       List existing diagram files in <arch-output-dir>
/arch-diagram --refresh    Re-read arch config and regenerate all existing diagrams
```

## Source Data

Always read `<arch-config-path>` before generating any diagram. This file is the single source of truth for system architecture. It must contain:

- `meta` - app name, version, last updated
- `nodes[]` - every system component with `id`, `label`, `layer`, `description`, `techDetails`, `filePaths`, `risks`
- `edges[]` - connections between nodes with `from`, `to`, `label`, `type`, `description`

Parse both arrays in full before planning the diagram layout.

## Output Files

Write generated diagrams to `<arch-output-dir>` using these names:

| View | Output file |
|---|---|
| full | `arch-full.html` |
| frontend | `arch-frontend.html` |
| backend | `arch-backend.html` |
| infra | `arch-infra.html` |
| game | `arch-game.html` |
| data-flow | `arch-data-flow.html` |

## Design System

### Color Coding (semantic - match component type exactly)

| Component type | Fill | Stroke | Fill opacity |
|---|---|---|---|
| User / external actor | `rgba(30, 41, 59, 0.5)` | `#94a3b8` | 0.5 |
| Frontend (SPA, Router, Context, Hook) | `rgba(8, 51, 68, 0.4)` | `#22d3ee` | 0.4 |
| Backend (Functions, services, APIs) | `rgba(6, 78, 59, 0.4)` | `#34d399` | 0.4 |
| Database (collections, tables) | `rgba(76, 29, 149, 0.4)` | `#a78bfa` | 0.4 |
| Infrastructure (hosting, platform services) | `rgba(120, 53, 15, 0.3)` | `#fbbf24` | 0.3 |
| Security (Auth, rules, webhooks) | `rgba(136, 19, 55, 0.4)` | `#fb7185` | 0.4 |
| Domain/business logic (core engine) | `rgba(124, 45, 18, 0.4)` | `#fb923c` | 0.4 |
| External service (third-party SaaS) | `rgba(30, 41, 59, 0.3)` | `#64748b` | 0.3 |

### Layer mapping from arch config

| `node.layer` value | Color category |
|---|---|
| `user` | User/external actor |
| `frontend` | Frontend |
| `context` | Frontend |
| `backend` | Backend |
| `database` | Database |
| `infra` | Infrastructure |
| `external` | External service |
| `game` or `core` | Domain/business logic |
| `security` | Security |

### Typography

- Font: `JetBrains Mono` (Google Fonts)
- Component label: `font-size="11"` `font-weight="600"` `fill="white"`
- Sublabel/tech detail: `font-size="9"` `fill="#94a3b8"`
- Accent text (URLs, ports): `font-size="8"` in component's stroke color
- Legend labels: `font-size="8"` `fill="#94a3b8"`
- Section boundary labels: `font-size="10"` `font-weight="600"` in boundary stroke color

### Component Shapes

**Standard component** (60px tall, width 110-160px depending on label length):
```svg
<rect x="X" y="Y" width="W" height="60" rx="6" fill="FILL" stroke="STROKE" stroke-width="1.5"/>
<text x="X+W/2" y="Y+20" fill="white" font-size="11" font-weight="600" text-anchor="middle">LABEL</text>
<text x="X+W/2" y="Y+36" fill="#94a3b8" font-size="9" text-anchor="middle">SUBLABEL</text>
<text x="X+W/2" y="Y+50" fill="STROKE" font-size="8" text-anchor="middle">ACCENT</text>
```

**Layer boundary** (dashed border around a group of components):
```svg
<rect x="X" y="Y" width="W" height="H" rx="12" fill="rgba(COLOR, 0.03)" stroke="STROKE" stroke-width="1" stroke-dasharray="8,4"/>
<text x="X+12" y="Y+16" fill="STROKE" font-size="10" font-weight="600">LAYER NAME</text>
```

**Security group** (tighter dashed border, rose color):
```svg
<rect x="X" y="Y" width="W" height="H" rx="8" fill="transparent" stroke="#fb7185" stroke-width="1" stroke-dasharray="4,4"/>
<text x="X+8" y="Y+12" fill="#fb7185" font-size="8">BOUNDARY LABEL</text>
```

### Arrows

Always define arrow markers in `<defs>`:
```svg
<marker id="arrowhead" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
  <polygon points="0 0, 10 3.5, 0 7" fill="#64748b"/>
</marker>
<marker id="arrowhead-cyan" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
  <polygon points="0 0, 10 3.5, 0 7" fill="#22d3ee"/>
</marker>
<marker id="arrowhead-emerald" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
  <polygon points="0 0, 10 3.5, 0 7" fill="#34d399"/>
</marker>
<marker id="arrowhead-violet" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
  <polygon points="0 0, 10 3.5, 0 7" fill="#a78bfa"/>
</marker>
```

Arrow types by `edge.type`:
- `realtime` / `subscription` -> use component's stroke color, solid line
- `auth` / `security` -> `#fb7185`, dashed `stroke-dasharray="5,5"`
- `api` / `http` -> `#22d3ee`, solid
- `trigger` / `event` -> `#fb923c`, dashed `stroke-dasharray="3,3"`
- `read` / `write` -> `#a78bfa`, solid
- default -> `#64748b`, solid

Arrow label placement: centered above the midpoint of the line, `font-size="9"` `fill="#94a3b8"`.

### Layout Rules (CRITICAL - bad layout breaks diagrams)

1. **Minimum 40px gap** between any two component boxes
2. **Components are 60px tall** minimum; add 16px per extra text line beyond sublabel
3. **Arrows must not cross component boxes** - route around them
4. **Legends go in top-right corner**, starting at x=750, y=60. Each row: 18px step. Legend must stay at least 20px below the lowest legend item's y coordinate before the next section.
5. **Layer boundaries** must have at least 20px padding around contained components
6. **Left-to-right flow** for request paths (users on left, database on right)
7. **Top-to-bottom** for security/auth flows
8. **viewBox**: start with `"0 0 1100 700"` for full; adjust for focused views
9. **No overlapping text** - always verify label positions don't collide

### SVG Canvas Sizes

| View | viewBox |
|---|---|
| full | `0 0 1200 750` |
| frontend | `0 0 1000 600` |
| backend | `0 0 1000 600` |
| infra | `0 0 1000 580` |
| game | `0 0 1100 680` |
| data-flow | `0 0 1200 600` |

---

## HTML Structure

Every output file must be self-contained - no external JS, no external CSS except Google Fonts. Use this exact structure:

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title><project-name> - [VIEW NAME] Architecture</title>
  <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600;700&display=swap" rel="stylesheet">
  <style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body { font-family: 'JetBrains Mono', monospace; background: #020617; min-height: 100vh; padding: 2rem; color: white; }
    .container { max-width: 1300px; margin: 0 auto; }
    .header { margin-bottom: 2rem; }
    .header-row { display: flex; align-items: center; gap: 1rem; margin-bottom: 0.5rem; }
    .pulse-dot { width: 12px; height: 12px; background: #22d3ee; border-radius: 50%; animation: pulse 2s infinite; }
    @keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.5; } }
    h1 { font-size: 1.5rem; font-weight: 700; letter-spacing: -0.025em; }
    .subtitle { color: #94a3b8; font-size: 0.875rem; margin-left: 1.75rem; }
    .nav-links { display: flex; gap: 1rem; margin-left: 1.75rem; margin-top: 0.75rem; flex-wrap: wrap; }
    .nav-links a { color: #22d3ee; font-size: 0.75rem; text-decoration: none; opacity: 0.7; }
    .nav-links a:hover { opacity: 1; }
    .nav-links a.active { opacity: 1; border-bottom: 1px solid #22d3ee; }
    .diagram-container { background: rgba(15, 23, 42, 0.5); border-radius: 1rem; border: 1px solid #1e293b; padding: 1.5rem; overflow-x: auto; }
    svg { width: 100%; min-width: 900px; display: block; }
    .cards { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 1rem; margin-top: 2rem; }
    .card { background: rgba(15, 23, 42, 0.5); border-radius: 0.75rem; border: 1px solid #1e293b; padding: 1.25rem; }
    .card-header { display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.75rem; }
    .card-dot { width: 8px; height: 8px; border-radius: 50%; }
    .card h3 { font-size: 0.875rem; font-weight: 600; }
    .card ul { list-style: none; color: #94a3b8; font-size: 0.75rem; }
    .card li { margin-bottom: 0.375rem; }
    .footer { text-align: center; margin-top: 1.5rem; color: #475569; font-size: 0.75rem; }
  </style>
</head>
<body>
  <div class="container">
    <div class="header">
      <div class="header-row">
        <div class="pulse-dot"></div>
        <h1><project-name> - [VIEW NAME] Architecture</h1>
      </div>
      <p class="subtitle">[One-line description of what this view shows]</p>
      <div class="nav-links">
        <a href="arch-full.html" [class="active" if this is full]>Full System</a>
        <a href="arch-frontend.html" [class="active" if this is frontend]>Frontend</a>
        <a href="arch-backend.html" [class="active" if this is backend]>Backend</a>
        <a href="arch-infra.html" [class="active" if this is infra]>Infrastructure</a>
        <a href="arch-game.html" [class="active" if this is game]>Domain Logic</a>
        <a href="arch-data-flow.html" [class="active" if this is data-flow]>Data Flow</a>
      </div>
    </div>

    <div class="diagram-container">
      <svg viewBox="[VIEWBOX]">
        <!-- Definitions -->
        <defs>
          [arrow markers]
          <pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse">
            <path d="M 40 0 L 0 0 0 40" fill="none" stroke="#1e293b" stroke-width="0.5"/>
          </pattern>
        </defs>

        <!-- Background Grid -->
        <rect width="100%" height="100%" fill="url(#grid)"/>

        <!-- [All SVG components and arrows here] -->

        <!-- Legend -->
        [Legend in top-right corner]
      </svg>
    </div>

    <!-- Info Cards -->
    <div class="cards">
      [3-4 cards with key facts, risks, tech details from arch config]
    </div>

    <p class="footer">
      <project-name> - [VIEW NAME] - Generated [DATE] from arch config v[VERSION]
    </p>
  </div>
</body>
</html>
```

---

## View Definitions

EDIT THIS SECTION for your project. The defaults below are illustrative; tune the column placements, layer boundaries, and key arrows to match your stack.

### `full` - Full System Overview

**Nodes to include:** All nodes from arch config.

**Layout (left to right, top to bottom by layer):**
1. **Left column** (x=30): External actors - end users, admins, third-party webhooks
2. **Layer boundary: Users** (dashed, slate) wraps column 1
3. **Second column** (x=160): Auth provider, SPA entry
4. **Layer boundary: Frontend** (dashed, cyan) wraps SPA + Router + Contexts
5. **Third column** (x=380): Domain/core packages, DB-access packages, shared types
6. **Fourth column** (x=600): Backend functions/services (grouped)
7. **Layer boundary: Backend** (dashed, emerald) wraps functions column
8. **Fifth column** (x=820): Database (grouped by collection/table)
9. **Layer boundary: Database** (dashed, violet) wraps DB column
10. **Bottom row** (y=580): Hosting, error monitoring, billing/SaaS
11. **Layer boundary: Infrastructure** (dashed, amber) wraps bottom row

**Key arrows to draw:**
- Users -> Auth (HTTPS, rose dashed)
- Auth -> SPA (JWT)
- SPA -> domain packages (imports)
- SPA -> DB-access packages (imports)
- DB-access -> Database (reads/writes, violet solid)
- DB triggers -> backend functions (orange dashed)
- Backend functions -> Database (writes, violet solid)
- Webhooks -> backend functions (rose dashed)
- SPA -> Hosting (served from, amber)
- SPA -> error monitoring (slate dashed)

### `frontend` - Frontend Layer

**Nodes to include:** All nodes with `layer` in `[user, frontend, context]` plus auth provider as external anchor.

**Layout:**
1. **Left**: Users, Admins (user layer)
2. **Center-left**: Auth provider
3. **Center**: SPA entry -> Router -> lazy-loaded Views
4. **Center-right**: AuthContext, primary domain Context (split into sub-contexts if applicable)
5. **Right**: Hooks (useAuth, useTeam/useProject/etc.)
6. **Bottom right**: domain core packages, DB-access packages as anchor boxes

Draw a layer boundary around the SPA ecosystem components.

**Key arrows:**
- Auth state-change flow from Auth provider -> AuthContext
- Context realtime subscriptions -> Database (right-exit arrow)
- Views using hooks (lazy load on demand)
- Context split into sub-contexts (if your app does this)

### `backend` - Backend (Functions / Services)

**Nodes to include:** All nodes with `layer` in `[backend, security]` plus Database as anchor.

**Layout:**
1. **Left**: Trigger sources - DB document writes, third-party webhooks, scheduled jobs
2. **Center**: Backend functions grouped by domain (auth triggers, user/profile sync, business logic, billing, audit)
3. **Right**: Database collections they write to
4. **Top**: Security rules (as a boundary overlay)

**Key arrows:**
- Webhook POSTs -> billing handler
- DB onWrite -> sync functions
- Business-logic functions -> DB updates
- Plan-sync -> tenant doc updates

### `infra` - Infrastructure

**Nodes to include:** All nodes with `layer` in `[infra, external]` plus the main apps as anchors.

**Layout:**
1. **Center-top**: Cloud platform boundary (amber dashed) containing: Hosting, Auth, Database, Functions, Storage
2. **Left outside boundary**: SPA (cyan, simplified)
3. **Right outside boundary**: External SaaS (billing, email, etc.)
4. **Bottom**: Error monitoring
5. **Top**: DNS / CDN layer

Show the cloud project as a large amber dashed boundary with all platform services inside it.

### `game` - Domain / Business Logic

(Rename this view to match your domain - e.g. `commerce`, `learning`, `pipeline`. The default below is for game-like apps.)

**Nodes to include:** All nodes related to your core domain logic.

**Layout (hub-and-spoke):**
1. **Center**: Core domain package (the hub)
2. **Top row**: Primary progression chain
3. **Middle row**: Secondary feature systems
4. **Bottom row**: Supporting systems
5. **Right**: Currencies / ledgers / state
6. **Left**: Configuration and tenant-specific data

Use orange (`#fb923c`) as the dominant color. Draw the core package as a larger central box.

### `data-flow` - Data Flow

**Purpose:** Show how a single user action flows through the entire system - from click to database and back.

**Layout (swimlane style, left to right):**

Draw horizontal swimlane boundaries (thin dashed lines) for:
1. **Browser** (top lane)
2. **SPA / Context Layer**
3. **Client SDK**
4. **Backend Functions**
5. **Database**

Trace two example flows (replace with flows that matter for your app):
- **Flow A: "User performs primary action"** (cyan arrows, solid)
- **Flow B: "Admin performs privileged action"** (orange arrows, dashed)

Number each step (1, 2, 3...) with small circle labels on the arrows.

---

## Diagram Generation Process

### Step 1 - Read source data

Read `<arch-config-path>` (full file). Extract all nodes, edges, and meta fields.

### Step 2 - Filter nodes for view

Apply the view-specific node filter from the View Definitions above.

### Step 3 - Plan layout on paper (in your reasoning)

Before writing SVG, mentally place every node:
- Assign (x, y) coordinates to each node
- Verify no two boxes overlap (check: box A right edge x+w < box B left edge x, with 40px min gap)
- Plan arrow routes to avoid crossing boxes
- Place legend in top-right, verify it doesn't overlap components

### Step 4 - Write the HTML file

Use the HTML Structure template above. Fill in:
- All SVG components at their planned coordinates
- All relevant arrows from `edges[]` (filtered to nodes in this view)
- Legend (only include colors actually used in this view)
- 3-4 info cards using `risks`, `scalingNotes`, and `techDetails` from arch config nodes
- Footer with today's date and arch config version

### Step 5 - Verify the output

After writing, mentally scan for:
- Any component label that would clip outside its box
- Any arrow endpoint that doesn't align with a box edge
- Any text overlap
- Legend items for colors not used in this diagram (remove them)

If issues found, rewrite the affected SVG section before reporting done.

### Step 6 - Report output

```
DIAGRAM GENERATED
==================
View: [view name]
File: <arch-output-dir>/[filename]
Nodes rendered: [N]
Connections: [N]
Open in browser: file://<arch-output-dir>/[filename]
```

If Chrome DevTools MCP is available and the browser is open, navigate to the file and take a screenshot to verify it renders correctly.

---

## Handling `--refresh`

1. Read the arch config
2. Check which `arch-*.html` files exist in `<arch-output-dir>`
3. Regenerate each existing file from scratch using current arch config data
4. Report which files were updated and what changed (new nodes, removed nodes, updated edges)

## Handling `--list`

List existing `arch-*.html` files in `<arch-output-dir>`. For each file found, report: filename, view type, file size, and last modified date.

## Handling `all`

Generate all six views in order: full -> frontend -> backend -> infra -> game -> data-flow. Report each one as it completes.

---

## Key Facts to Encode

When writing info cards, pull from your arch config's `risks[]`, `scalingNotes`, and `techDetails` fields rather than inventing details. Cards should be specific and traceable to the source config.

---

## Quality Checklist

Before writing any diagram file, confirm:

- [ ] All node labels fit inside their boxes (test: label character count * ~7px < box width)
- [ ] No arrows cross component boxes - route around via waypoints if needed
- [ ] Layer boundaries have at least 20px padding around contents
- [ ] Legend uses only colors that appear in this diagram
- [ ] Info cards draw from actual arch config `risks[]` and `scalingNotes` fields
- [ ] Nav links point to correct filenames with correct `active` class on current view
- [ ] Footer shows today's date and arch config version
- [ ] File is self-contained - opening in browser requires no server
