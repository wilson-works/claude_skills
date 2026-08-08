#!/usr/bin/env python3
"""agent-org comms CLI.

A token-efficient SQLite-backed message bus + path-claim ledger for the
agent-org hierarchy. Seven branches (CTO / CFO / COO / CAO / EA-rep / CPA-attest / CMO),
tiered channels, hard ACL.

Channels:
    CTO branch
        c-suite             James, John, Tim
        dept-heads          Tim, Cindy, Gavin, Diana, Rachel, Josh
        dev-floor           Cindy, Gavin, Diana, Rachel, Josh + all juniors
    CFO branch
        cfo-suite           Elle, Soph
        cfo-dept-heads      Soph, Hal, Imani, Anya, Nadia
        finance-floor       Hal, Imani, Anya, Nadia + 8 seniors
    COO branch
        coo-suite           Mara, Jas
        coo-dept-heads      Jas, Roz
        ops-floor           Roz + 2 HR seniors
    CAO branch (Chief Awareness Officer / AI oversight)
        cao-suite           Amelia, Victor, Elena
        cao-dept-heads      Elena, Clay, Camille, Cole, Wren
        cao-floor           Clay, Camille, Cole, Wren (+ future juniors)
    EA-rep branch (Enrolled Agent / IRS representation)
        ea-rep-suite        Marisol, Anika
        ea-rep-dept-heads   Anika, Otto, Kira, Mateo
        ea-rep-floor        Otto, Kira, Mateo + 3 seniors
    CPA-attest branch (Audit / Attest / Assurance)
        cpa-suite           Everett, Juno
        cpa-dept-heads      Juno, Priscilla, Mason, Saira
        cpa-floor           Priscilla, Mason, Saira + 3 seniors
    CMO branch (Marketing)
        cmo-suite           Margot, Rina
        cmo-dept-heads      Rina, Sela, Rocco, Yara, Arlo
        cmo-floor           Sela, Rocco, Yara, Arlo + 4 seniors
    Cross-branch
        exec-eas            Tim, Soph, Jas, Elena, Anika, Juno, Rina (only)

Token discipline:
    Default `read` output is one line per message: "#42 14:23 cindy->john (subj)".
    Bodies only print under --verbose. Default --limit is 20.
    Bodies are capped at MAX_BODY_CHARS on post (truncated, not rejected).

Database location:
    Resolved in this order:
      1) AGENT_ORG_DB env var
      2) <repo>/.claude/comms.db where <repo> is the nearest ancestor with .git
      3) ./.claude/comms.db relative to cwd

CLI:
    comms.py post <channel> <from> --subject TEXT [--to A] [--thread ID] [--wo WO] BODY
    comms.py read <channel> <as_agent> [--since ID|--unread] [--limit N] [--verbose] [--mine]
    comms.py thread <id> <as_agent> [--verbose]
    comms.py inbox <as_agent> [--unread] [--limit N]
    comms.py mark-read <channel> <as_agent> [--up-to ID]
    comms.py claim <path> <as_agent> [--wo WO]
    comms.py release (--path PATH | --id ID) <as_agent>
    comms.py claims [--active] [--by AGENT] [--for-path PATH]
    comms.py whoami <agent>
    comms.py stats
    comms.py archive --before YYYY-MM-DD
    comms.py init        Force-create the DB (normally lazy on first use)
"""

from __future__ import annotations

import argparse
import os
import sqlite3
import sys
import textwrap
from datetime import datetime
from fnmatch import fnmatch
from pathlib import Path

# ---------------------------------------------------------------------------
# Roster + ACL. The org is fixed; only the *project paths* are configurable
# (see org.config.json, consumed by path_guard.py — not here).
# ---------------------------------------------------------------------------

CHANNELS = (
    # CTO branch (existing)
    "c-suite",
    "dept-heads",
    "dev-floor",
    # CFO branch
    "cfo-suite",
    "cfo-dept-heads",
    "finance-floor",
    # COO branch
    "coo-suite",
    "coo-dept-heads",
    "ops-floor",
    # CAO branch (Chief Awareness Officer / AI oversight)
    "cao-suite",
    "cao-dept-heads",
    "cao-floor",
    # EA-rep branch (Enrolled Agent / IRS representation)
    "ea-rep-suite",
    "ea-rep-dept-heads",
    "ea-rep-floor",
    # CPA-attest branch (Audit / Attestation / Assurance)
    "cpa-suite",
    "cpa-dept-heads",
    "cpa-floor",
    # CMO branch (Marketing)
    "cmo-suite",
    "cmo-dept-heads",
    "cmo-floor",
    # Cross-branch EA channel
    "exec-eas",
)

ACL: dict[str, set[str]] = {
    # ---- CTO branch ----
    # C-suite (Opus)
    "james": {"c-suite"},  # CTO
    "john": {"c-suite"},  # Chief Engineer
    # Bridge (Opus) — Tim is on c-suite + dept-heads, plus the cross-branch exec-eas
    "tim": {"c-suite", "dept-heads", "exec-eas"},  # Exec Assistant
    # Department heads (Opus) — bridge dept-heads <-> dev-floor
    "cindy": {"dept-heads", "dev-floor"},  # Backend
    "gavin": {"dept-heads", "dev-floor"},  # Frontend
    "diana": {"dept-heads", "dev-floor"},  # Database
    "rachel": {"dept-heads", "dev-floor"},  # QA
    "josh": {"dept-heads", "dev-floor"},  # API
    # Juniors (Sonnet) — confined to dev-floor
    "marcus": {"dev-floor"},
    "priya": {"dev-floor"},  # backend
    "ava": {"dev-floor"},
    "kai": {"dev-floor"},  # frontend
    "leo": {"dev-floor"},
    "nora": {"dev-floor"},  # database
    "owen": {"dev-floor"},
    "maya": {"dev-floor"},  # qa
    "felix": {"dev-floor"},
    "zara": {"dev-floor"},  # api
    # ---- CFO branch ----
    "elle": {"cfo-suite"},  # CFO
    # Bridge (Opus) — Sophia is on cfo-suite + cfo-dept-heads + exec-eas
    "soph": {"cfo-suite", "cfo-dept-heads", "exec-eas"},  # CFO Exec Assistant
    # Finance heads (Opus) — bridge cfo-dept-heads <-> finance-floor
    "hal": {"cfo-dept-heads", "finance-floor"},  # Controller
    "imani": {"cfo-dept-heads", "finance-floor"},  # Treasurer
    "anya": {"cfo-dept-heads", "finance-floor"},  # Tax Director
    "nadia": {"cfo-dept-heads", "finance-floor"},  # FP&A Director
    # Finance seniors (Sonnet) — confined to finance-floor
    "lila": {"finance-floor"},  # Controller: AP/AR
    "theo": {"finance-floor"},  # Controller: rev rec / JEs
    "tomas": {"finance-floor"},  # Treasury: cash position
    "bea": {"finance-floor"},  # Treasury: bill-pay / WC
    "reyna": {"finance-floor"},  # Tax: federal
    "devon": {"finance-floor"},  # Tax: state + notices
    "eli": {"finance-floor"},  # FP&A: variance
    "quinn": {"finance-floor"},  # FP&A: forecast
    # ---- COO branch ----
    "mara": {"coo-suite"},  # COO
    # Bridge (Opus) — Jasper is on coo-suite + coo-dept-heads + exec-eas
    "jas": {"coo-suite", "coo-dept-heads", "exec-eas"},  # COO Exec Assistant
    # Ops head (Opus) — bridge coo-dept-heads <-> ops-floor
    "roz": {"coo-dept-heads", "ops-floor"},  # HR Director
    # Ops seniors (Sonnet) — confined to ops-floor
    "lena": {"ops-floor"},  # HR: compliance / CPE
    "chidi": {"ops-floor"},  # HR: recruiting / onboarding
    # ---- CAO branch (Chief Awareness Officer / AI oversight) ----
    "amelia": {"cao-suite"},  # Chief Awareness Officer
    "victor": {"cao-suite"},  # VP of AI (peer of Amelia in cao-suite)
    # Bridge (Opus) — Elena is on cao-suite + cao-dept-heads + exec-eas
    "elena": {"cao-suite", "cao-dept-heads", "exec-eas"},  # CAO Exec Assistant
    # CAO heads (Opus) — bridge cao-dept-heads <-> cao-floor
    "clay": {"cao-dept-heads", "cao-floor"},  # Claude Dept (model-ops)
    "camille": {"cao-dept-heads", "cao-floor"},  # Copy Dept
    "cole": {"cao-dept-heads", "cao-floor"},  # Coding Dept (CAO branch)
    "wren": {"cao-dept-heads", "cao-floor"},  # Wellness Officer
    # ---- EA-rep branch (Enrolled Agent / IRS representation) ----
    "marisol": {"ea-rep-suite"},  # Director of Representation
    # Bridge (Opus) — Anika is on ea-rep-suite + ea-rep-dept-heads + exec-eas
    "anika": {"ea-rep-suite", "ea-rep-dept-heads", "exec-eas"},  # DOR Exec Assistant
    # EA-rep heads (Opus) — bridge ea-rep-dept-heads <-> ea-rep-floor
    "otto": {"ea-rep-dept-heads", "ea-rep-floor"},  # Examinations & Appeals
    "kira": {"ea-rep-dept-heads", "ea-rep-floor"},  # Collections
    "mateo": {"ea-rep-dept-heads", "ea-rep-floor"},  # Notices & E-Services
    # EA-rep seniors (Sonnet) — confined to ea-rep-floor
    "tess": {"ea-rep-floor"},  # Senior Rep Specialist - Exams
    "rafa": {"ea-rep-floor"},  # Senior Rep Specialist - Collections
    "ines": {"ea-rep-floor"},  # Senior Rep Specialist - Notices/E-Services
    # ---- CPA-attest branch (Audit / Attest / Assurance) ----
    "everett": {"cpa-suite"},  # Chief Audit Partner
    # Bridge (Opus) — Juno is on cpa-suite + cpa-dept-heads + exec-eas
    "juno": {"cpa-suite", "cpa-dept-heads", "exec-eas"},  # CAP Exec Assistant
    # CPA-attest heads (Opus) — bridge cpa-dept-heads <-> cpa-floor
    "priscilla": {"cpa-dept-heads", "cpa-floor"},  # Audit (AU-C / SAS)
    "mason": {"cpa-dept-heads", "cpa-floor"},  # Attest (SSAE/SSARS/SOC)
    "saira": {"cpa-dept-heads", "cpa-floor"},  # Quality & Independence
    # CPA-attest seniors (Sonnet) — confined to cpa-floor
    "niall": {"cpa-floor"},  # Senior Auditor
    "orla": {"cpa-floor"},  # Senior Attest Specialist
    "finn": {"cpa-floor"},  # Senior Quality Specialist
    # ---- CMO branch (Marketing) ----
    "margot": {"cmo-suite"},  # CMO
    # Bridge (Opus) — Rina is on cmo-suite + cmo-dept-heads + exec-eas
    "rina": {"cmo-suite", "cmo-dept-heads", "exec-eas"},  # CMO Exec Assistant
    # CMO heads (Opus) — bridge cmo-dept-heads <-> cmo-floor
    "sela": {"cmo-dept-heads", "cmo-floor"},  # Brand & Positioning
    "rocco": {"cmo-dept-heads", "cmo-floor"},  # Demand & Performance
    "yara": {"cmo-dept-heads", "cmo-floor"},  # Content & Earned
    "arlo": {"cmo-dept-heads", "cmo-floor"},  # Analytics & MarOps
    # CMO seniors (Sonnet) — confined to cmo-floor
    "fern": {"cmo-floor"},  # Senior Brand Specialist
    "tate": {"cmo-floor"},  # Senior Demand Specialist
    "luca": {"cmo-floor"},  # Senior Content Specialist
    "iggy": {"cmo-floor"},  # Senior Analytics Specialist
}

DEPARTMENT_OF: dict[str, str] = {
    # CTO branch — coding departments (path_guard enforces ownership)
    "cindy": "backend",
    "marcus": "backend",
    "priya": "backend",
    "gavin": "frontend",
    "ava": "frontend",
    "kai": "frontend",
    "diana": "database",
    "leo": "database",
    "nora": "database",
    "rachel": "qa",
    "owen": "qa",
    "maya": "qa",
    "josh": "api",
    "felix": "api",
    "zara": "api",
    # CFO branch — advisory departments (no Edit/Write; path_guard does not enforce)
    "hal": "controller",
    "lila": "controller",
    "theo": "controller",
    "imani": "treasury",
    "tomas": "treasury",
    "bea": "treasury",
    "anya": "tax",
    "reyna": "tax",
    "devon": "tax",
    "nadia": "fpa",
    "eli": "fpa",
    "quinn": "fpa",
    # COO branch — advisory departments
    "roz": "hr",
    "lena": "hr",
    "chidi": "hr",
    # CAO branch — mixed (copy + coding-cao have Edit/Write; claude-ops + wellness are advisory)
    "clay": "claude-ops",
    "camille": "copy",
    "cole": "coding-cao",
    "wren": "wellness",
    # EA-rep branch — advisory departments
    "otto": "exams-rep",
    "tess": "exams-rep",
    "kira": "collections-rep",
    "rafa": "collections-rep",
    "mateo": "notices-rep",
    "ines": "notices-rep",
    # CPA-attest branch — advisory departments
    "priscilla": "audit",
    "niall": "audit",
    "mason": "attest",
    "orla": "attest",
    "saira": "quality",
    "finn": "quality",
    # CMO branch — mixed (demand + content have Edit/Write for marketing-owned paths; brand + analytics advisory)
    "sela": "brand",
    "fern": "brand",
    "rocco": "demand",
    "tate": "demand",
    "yara": "content",
    "luca": "content",
    "arlo": "analytics-mar",
    "iggy": "analytics-mar",
}

ROLE_OF: dict[str, str] = {
    # CTO branch
    "james": "CTO",
    "john": "Chief Engineer",
    "tim": "Executive Assistant",
    "cindy": "Backend Lead",
    "gavin": "Frontend Lead",
    "diana": "Database Lead",
    "rachel": "QA Lead",
    "josh": "API Lead",
    "marcus": "Backend Junior",
    "priya": "Backend Junior",
    "ava": "Frontend Junior",
    "kai": "Frontend Junior",
    "leo": "Database Junior",
    "nora": "Database Junior",
    "owen": "QA Junior",
    "maya": "QA Junior",
    "felix": "API Junior",
    "zara": "API Junior",
    # CFO branch
    "elle": "CFO",
    "soph": "CFO Executive Assistant",
    "hal": "Controller",
    "imani": "Treasurer",
    "anya": "Tax Director",
    "nadia": "FP&A Director",
    "lila": "Senior Accountant (AP/AR)",
    "theo": "Senior Accountant (Rev Rec)",
    "tomas": "Senior Treasury Analyst (Cash)",
    "bea": "Senior Treasury Analyst (Working Capital)",
    "reyna": "Senior Tax Specialist (Federal)",
    "devon": "Senior Tax Specialist (State + Notices)",
    "eli": "Senior FP&A Analyst (Variance)",
    "quinn": "Senior FP&A Analyst (Forecast)",
    # COO branch
    "mara": "COO",
    "jas": "COO Executive Assistant",
    "roz": "HR Director",
    "lena": "Senior HR Specialist (Compliance / CPE)",
    "chidi": "Senior HR Specialist (Recruiting / Onboarding)",
    # CAO branch
    "amelia": "Chief Awareness Officer",
    "victor": "VP of AI",
    "elena": "CAO Executive Assistant",
    "clay": "Claude Dept Head",
    "camille": "Copy Dept Head",
    "cole": "Coding Dept Head (CAO)",
    "wren": "Wellness Officer",
    # EA-rep branch
    "marisol": "Director of Representation",
    "anika": "DOR Executive Assistant",
    "otto": "Examinations & Appeals Head",
    "kira": "Collections Head",
    "mateo": "Notices & E-Services Head",
    "tess": "Senior Rep Specialist (Exams)",
    "rafa": "Senior Rep Specialist (Collections)",
    "ines": "Senior Rep Specialist (Notices / E-Services)",
    # CPA-attest branch
    "everett": "Chief Audit Partner",
    "juno": "CAP Executive Assistant",
    "priscilla": "Audit Head",
    "mason": "Attest Head",
    "saira": "Quality & Independence Head",
    "niall": "Senior Auditor",
    "orla": "Senior Attest Specialist",
    "finn": "Senior Quality Specialist",
    # CMO branch
    "margot": "CMO",
    "rina": "CMO Executive Assistant",
    "sela": "Brand & Positioning Head",
    "rocco": "Demand & Performance Head",
    "yara": "Content & Earned Head",
    "arlo": "Analytics & MarOps Head",
    "fern": "Senior Brand Specialist",
    "tate": "Senior Demand Specialist",
    "luca": "Senior Content Specialist",
    "iggy": "Senior Analytics Specialist",
}

MAX_BODY_CHARS = 2000
SCHEMA_PATH = Path(__file__).parent / "schema.sql"

# How long SQLite waits for a lock before raising "database is locked".
# The CLI is not latency-sensitive, so it waits generously. path_guard.py runs
# as a PreToolUse hook on every Write/Edit and uses a shorter one on purpose.
BUSY_TIMEOUT_MS = 5000

# Default lifetime of a path claim. Harvested from crew/SKILL.md:74-76, which
# already solved this: a session unheard-from for 30 min is presumed dead and
# its owned files are released. comms.py has no heartbeat, so the claim itself
# carries the deadline. Override globally with AGENT_ORG_CLAIM_TTL_MIN, or per
# claim with `claim --ttl <minutes>`. 0 means "never expires".
CLAIM_TTL_MINUTES = 30

# Wall-clock format used by every timestamp column in schema.sql. Fixed-width
# UTC, so lexicographic comparison is chronological comparison. Deadlines are
# computed by SQLite, not Python, so there is no clock skew between the two.
SQL_NOW = "strftime('%Y-%m-%dT%H:%M:%fZ', 'now')"
SQL_NOW_PLUS = "strftime('%Y-%m-%dT%H:%M:%fZ', 'now', ?)"  # ? = '+30 minutes'

# ---------------------------------------------------------------------------
# DB plumbing
# ---------------------------------------------------------------------------


def find_repo_root(start: Path) -> Path | None:
    cur = start.resolve()
    for p in (cur, *cur.parents):
        if (p / ".git").exists():
            return p
    return None


def resolve_db_path() -> Path:
    env = os.environ.get("AGENT_ORG_DB")
    if env:
        return Path(env)
    repo = find_repo_root(Path.cwd())
    base = repo if repo else Path.cwd()
    return base / ".claude" / "comms.db"


def connect(db_path: Path) -> sqlite3.Connection:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    fresh = not db_path.exists()
    conn = sqlite3.connect(str(db_path))
    # busy_timeout FIRST: `PRAGMA journal_mode = WAL` itself takes a lock, so a
    # concurrent writer would otherwise fail here before any retry policy is in
    # force. Without this, concurrent lanes get an immediate "database is
    # locked" instead of waiting their turn.
    conn.execute(f"PRAGMA busy_timeout = {BUSY_TIMEOUT_MS}")
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA journal_mode = WAL")
    if fresh or _missing_tables(conn):
        schema = SCHEMA_PATH.read_text(encoding="utf-8")
        conn.executescript(schema)
        conn.commit()
    else:
        _migrate(conn)
    return conn


def _missing_tables(conn: sqlite3.Connection) -> bool:
    rows = conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
    have = {r[0] for r in rows}
    return not {"messages", "read_state", "claims", "audit"}.issubset(have)


def _migrate(conn: sqlite3.Connection) -> None:
    """Bring an existing comms.db up to the current schema. Additive only.

    Both steps are idempotent and safe to run on every connect.
    """
    cols = {r[1] for r in conn.execute("PRAGMA table_info(claims)").fetchall()}
    if "expires_at" not in cols:
        # Nullable, no default: every pre-existing claim stays "never expires".
        conn.execute("ALTER TABLE claims ADD COLUMN expires_at TEXT")
        conn.commit()
    try:
        conn.execute(
            "CREATE UNIQUE INDEX IF NOT EXISTS idx_claims_one_active_per_path "
            "ON claims(path) WHERE status = 'active'"
        )
        conn.commit()
    except sqlite3.IntegrityError:
        # The DB already holds duplicate ACTIVE claims on one path - exactly the
        # lost-race this index exists to prevent, recorded before the fix landed.
        # Do not mutate anyone's claims to force the index through; say so loudly
        # and continue. BEGIN IMMEDIATE in cmd_claim still serializes new claims.
        conn.rollback()
        sys.stderr.write(
            "comms: WARNING - could not create idx_claims_one_active_per_path; "
            "the claims table already contains duplicate active rows for one path.\n"
            "  Inspect: SELECT path, COUNT(*) FROM claims WHERE status='active' "
            "GROUP BY path HAVING COUNT(*) > 1;\n"
            "  Resolve those claims (release/expire the stale ones), then reconnect.\n"
        )


# ---------------------------------------------------------------------------
# ACL + validation
# ---------------------------------------------------------------------------


def require_known_agent(agent: str) -> None:
    if agent not in ACL:
        die(f"unknown agent '{agent}'. Roster: {', '.join(sorted(ACL))}")


def require_channel(channel: str) -> None:
    if channel not in CHANNELS:
        die(f"unknown channel '{channel}'. Channels: {', '.join(CHANNELS)}")


def require_acl(agent: str, channel: str, action: str) -> None:
    require_known_agent(agent)
    require_channel(channel)
    if channel not in ACL[agent]:
        die(
            f"ACL DENY: {agent} ({ROLE_OF[agent]}) cannot {action} on '{channel}'. "
            f"Allowed channels: {', '.join(sorted(ACL[agent])) or 'none'}"
        )


def die(msg: str, code: int = 2) -> None:
    sys.stderr.write(f"comms: {msg}\n")
    sys.exit(code)


def audit(conn: sqlite3.Connection, agent: str, action: str, detail: str = "") -> None:
    conn.execute(
        "INSERT INTO audit (agent, action, detail) VALUES (?, ?, ?)",
        (agent, action, detail[:500]),
    )


# ---------------------------------------------------------------------------
# Output formatting (token-efficient by default)
# ---------------------------------------------------------------------------


def short_time(iso: str) -> str:
    # 2026-05-06T14:23:01.123Z -> 05-06 14:23
    try:
        dt = datetime.fromisoformat(iso.replace("Z", "+00:00"))
        return dt.strftime("%m-%d %H:%M")
    except ValueError:
        return iso[:16]


def fmt_row(row: sqlite3.Row, verbose: bool) -> str:
    target = row["to_agent"] or row["channel"]
    head = (
        f"#{row['id']} {short_time(row['posted_at'])} "
        f"{row['from_agent']}->{target} ({row['subject']})"
    )
    if row["work_order"]:
        head += f" [{row['work_order']}]"
    if not verbose:
        return head
    body = textwrap.fill(row["body"], width=78, initial_indent="  ", subsequent_indent="  ")
    return f"{head}\n{body}"


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------


def cmd_post(args: argparse.Namespace) -> int:
    require_acl(args.from_agent, args.channel, "post")
    if args.to:
        require_known_agent(args.to)
    body = args.body
    if body == "-":
        body = sys.stdin.read()
    if len(body) > MAX_BODY_CHARS:
        body = body[:MAX_BODY_CHARS] + "\n…[truncated]"

    db = resolve_db_path()
    conn = connect(db)
    cur = conn.execute(
        """INSERT INTO messages
              (channel, from_agent, to_agent, thread_id, subject, body, work_order)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (args.channel, args.from_agent, args.to, args.thread, args.subject, body, args.wo),
    )
    audit(conn, args.from_agent, "post", f"#{cur.lastrowid} {args.channel} -> {args.to or '*'}")
    conn.commit()
    print(f"posted #{cur.lastrowid} on {args.channel}")
    return 0


def cmd_read(args: argparse.Namespace) -> int:
    require_acl(args.as_agent, args.channel, "read")
    db = resolve_db_path()
    conn = connect(db)
    conn.row_factory = sqlite3.Row

    since = args.since
    if args.unread:
        cur = conn.execute(
            "SELECT last_read_id FROM read_state WHERE agent = ? AND channel = ?",
            (args.as_agent, args.channel),
        ).fetchone()
        since = cur["last_read_id"] if cur else 0

    where = ["channel = ?"]
    params: list = [args.channel]
    if since is not None:
        where.append("id > ?")
        params.append(since)
    if args.mine:
        where.append("(to_agent = ? OR to_agent IS NULL)")
        params.append(args.as_agent)

    sql = f"SELECT * FROM messages WHERE {' AND '.join(where)} " f"ORDER BY id DESC LIMIT ?"
    params.append(args.limit)
    rows = list(reversed(conn.execute(sql, params).fetchall()))

    if not rows:
        print(f"(no messages on {args.channel}" + (f" since #{since}" if since else "") + ")")
        return 0

    for row in rows:
        print(fmt_row(row, args.verbose))

    # advance read cursor to the newest message returned
    newest = max(r["id"] for r in rows)
    conn.execute(
        """INSERT INTO read_state (agent, channel, last_read_id)
           VALUES (?, ?, ?)
           ON CONFLICT(agent, channel) DO UPDATE
             SET last_read_id = MAX(last_read_id, excluded.last_read_id)""",
        (args.as_agent, args.channel, newest),
    )
    audit(conn, args.as_agent, "read", f"{args.channel} up_to #{newest} ({len(rows)} msgs)")
    conn.commit()
    return 0


def cmd_thread(args: argparse.Namespace) -> int:
    require_known_agent(args.as_agent)
    db = resolve_db_path()
    conn = connect(db)
    conn.row_factory = sqlite3.Row

    root = conn.execute("SELECT * FROM messages WHERE id = ?", (args.id,)).fetchone()
    if not root:
        die(f"no message #{args.id}")
    require_acl(args.as_agent, root["channel"], "read")

    rows = conn.execute(
        """SELECT * FROM messages
           WHERE id = ? OR thread_id = ?
           ORDER BY id ASC""",
        (args.id, args.id),
    ).fetchall()
    for row in rows:
        print(fmt_row(row, verbose=True))
    return 0


def cmd_inbox(args: argparse.Namespace) -> int:
    require_known_agent(args.as_agent)
    db = resolve_db_path()
    conn = connect(db)
    conn.row_factory = sqlite3.Row

    channels = sorted(ACL[args.as_agent])
    placeholders = ",".join("?" * len(channels))
    where = [f"channel IN ({placeholders})", "to_agent = ?"]
    params: list = [*channels, args.as_agent]

    if args.unread:
        # filter against per-channel last_read_id
        cursors = {
            r["channel"]: r["last_read_id"]
            for r in conn.execute(
                "SELECT channel, last_read_id FROM read_state WHERE agent = ?",
                (args.as_agent,),
            ).fetchall()
        }
        # build per-channel OR clauses
        chan_clauses = []
        for c in channels:
            chan_clauses.append("(channel = ? AND id > ?)")
            params.extend([c, cursors.get(c, 0)])
        where = [f"({' OR '.join(chan_clauses)})", "to_agent = ?"]
        params.append(args.as_agent)

    sql = f"SELECT * FROM messages WHERE {' AND '.join(where)} " f"ORDER BY id DESC LIMIT ?"
    params.append(args.limit)
    rows = list(reversed(conn.execute(sql, params).fetchall()))

    if not rows:
        print(f"(inbox empty for {args.as_agent})")
        return 0
    for row in rows:
        print(fmt_row(row, verbose=False))
    return 0


def cmd_mark_read(args: argparse.Namespace) -> int:
    require_acl(args.as_agent, args.channel, "read")
    db = resolve_db_path()
    conn = connect(db)
    up_to = args.up_to
    if up_to is None:
        cur = conn.execute(
            "SELECT MAX(id) AS m FROM messages WHERE channel = ?",
            (args.channel,),
        ).fetchone()
        up_to = cur[0] or 0
    conn.execute(
        """INSERT INTO read_state (agent, channel, last_read_id)
           VALUES (?, ?, ?)
           ON CONFLICT(agent, channel) DO UPDATE
             SET last_read_id = MAX(last_read_id, excluded.last_read_id)""",
        (args.as_agent, args.channel, up_to),
    )
    conn.commit()
    print(f"marked {args.channel} read up to #{up_to} for {args.as_agent}")
    return 0


def claim_ttl_minutes(explicit: int | None = None) -> int:
    """Minutes a new claim stays active. 0 means "never expires".

    Negatives are rejected rather than clamped: silently turning `--ttl -5` into
    an immortal claim is the opposite of what the typo meant.
    """
    if explicit is not None:
        if explicit < 0:
            die("--ttl must be >= 0 minutes (0 means the claim never expires)")
        return explicit
    env = os.environ.get("AGENT_ORG_CLAIM_TTL_MIN")
    if env:
        try:
            minutes = int(env)
        except ValueError:
            die(f"AGENT_ORG_CLAIM_TTL_MIN must be an integer number of minutes, got '{env}'")
        if minutes < 0:
            die(f"AGENT_ORG_CLAIM_TTL_MIN must be >= 0 minutes, got '{env}'")
        return minutes
    return CLAIM_TTL_MINUTES


def sweep_expired(conn: sqlite3.Connection) -> int:
    """Retire active claims that have outlived their expires_at. Returns count.

    NULL expires_at means "never expires" - that is every row written before the
    column existed, so an upgrade never mass-expires anyone's claims.
    """
    return conn.execute(
        f"""UPDATE claims SET status='expired', released_at={SQL_NOW}
            WHERE status='active'
              AND expires_at IS NOT NULL
              AND expires_at <= {SQL_NOW}"""
    ).rowcount


def cmd_claim(args: argparse.Namespace) -> int:
    require_known_agent(args.as_agent)
    db = resolve_db_path()
    conn = connect(db)
    conn.row_factory = sqlite3.Row
    ttl = claim_ttl_minutes(getattr(args, "ttl", None))
    modifier = f"+{ttl} minutes" if ttl else None

    # The whole check-then-insert has to be ONE transaction. BEGIN IMMEDIATE
    # takes the write lock up front, so a second claimant blocks here (up to
    # busy_timeout) instead of reading a stale "no conflict" and inserting a
    # duplicate. isolation_level=None turns off pysqlite's implicit BEGIN so the
    # transaction boundaries below are the only ones in play.
    conn.isolation_level = None
    try:
        conn.execute("BEGIN IMMEDIATE")
    except sqlite3.OperationalError as exc:
        die(
            f"CLAIM UNAVAILABLE: could not acquire the claims write lock within "
            f"{BUSY_TIMEOUT_MS} ms ({exc}). Another agent is mid-claim. Retry.",
            code=3,
        )

    try:
        swept = sweep_expired(conn)

        # detect overlap with existing active claims by other agents
        existing = conn.execute(
            "SELECT id, agent, path FROM claims WHERE status = 'active'"
        ).fetchall()
        mine = None
        for row in existing:
            if row["agent"] == args.as_agent:
                # Re-claiming a path you already hold is a refresh, not a
                # conflict. It has to be handled explicitly now that the DB
                # enforces one active claim per path.
                if row["path"] == args.path:
                    mine = row
                continue
            if _paths_overlap(args.path, row["path"]):
                conn.execute("ROLLBACK")
                die(
                    f"CLAIM CONFLICT: '{args.path}' overlaps with claim "
                    f"#{row['id']} ('{row['path']}') held by {row['agent']}. "
                    f"Coordinate on dev-floor or wait for release.",
                    code=3,
                )

        if mine is not None:
            if modifier:
                conn.execute(
                    f"UPDATE claims SET expires_at = {SQL_NOW_PLUS} WHERE id = ?",
                    (modifier, mine["id"]),
                )
            else:
                conn.execute("UPDATE claims SET expires_at = NULL WHERE id = ?", (mine["id"],))
            audit(conn, args.as_agent, "claim-refresh", f"#{mine['id']} {args.path}")
            conn.execute("COMMIT")
            print(
                f"claim #{mine['id']} still active for {args.as_agent}: {args.path}"
                + (f" (renewed {ttl}m)" if ttl else " (no expiry)")
                + (f"; {swept} expired claim(s) swept" if swept else "")
            )
            return 0

        try:
            if modifier:
                cur = conn.execute(
                    f"""INSERT INTO claims (path, agent, work_order, expires_at)
                        VALUES (?, ?, ?, {SQL_NOW_PLUS})""",
                    (args.path, args.as_agent, args.wo, modifier),
                )
            else:
                cur = conn.execute(
                    """INSERT INTO claims (path, agent, work_order, expires_at)
                       VALUES (?, ?, ?, NULL)""",
                    (args.path, args.as_agent, args.wo),
                )
        except sqlite3.IntegrityError:
            # idx_claims_one_active_per_path fired: somebody else's claim on this
            # exact path landed between our read and our write. Report it as a
            # denial, not a traceback.
            holder = conn.execute(
                "SELECT id, agent FROM claims WHERE status='active' AND path = ?",
                (args.path,),
            ).fetchone()
            conn.execute("ROLLBACK")
            if holder is None:
                die(f"CLAIM DENIED: '{args.path}' is already claimed.", code=3)
            die(
                f"CLAIM DENIED: '{args.path}' is already held by {holder['agent']} "
                f"(claim #{holder['id']}). Coordinate on dev-floor or wait for release.",
                code=3,
            )
        audit(conn, args.as_agent, "claim", f"#{cur.lastrowid} {args.path}")
        conn.execute("COMMIT")
    except sqlite3.OperationalError as exc:
        try:
            conn.execute("ROLLBACK")
        except sqlite3.Error:
            pass
        die(f"CLAIM FAILED: {exc}. Retry.", code=3)

    print(
        f"claim #{cur.lastrowid} active for {args.as_agent}: {args.path}"
        + (f" (expires in {ttl}m)" if ttl else " (no expiry)")
        + (f"; {swept} expired claim(s) swept" if swept else "")
    )
    return 0


def cmd_release(args: argparse.Namespace) -> int:
    require_known_agent(args.as_agent)
    db = resolve_db_path()
    conn = connect(db)
    if args.id:
        n = conn.execute(
            """UPDATE claims SET status='released',
                 released_at=strftime('%Y-%m-%dT%H:%M:%fZ', 'now')
               WHERE id = ? AND agent = ? AND status='active'""",
            (args.id, args.as_agent),
        ).rowcount
    else:
        n = conn.execute(
            """UPDATE claims SET status='released',
                 released_at=strftime('%Y-%m-%dT%H:%M:%fZ', 'now')
               WHERE path = ? AND agent = ? AND status='active'""",
            (args.path, args.as_agent),
        ).rowcount
    audit(conn, args.as_agent, "release", f"id={args.id} path={args.path} n={n}")
    conn.commit()
    print(f"released {n} claim(s) for {args.as_agent}")
    return 0 if n else 1


def cmd_claims(args: argparse.Namespace) -> int:
    db = resolve_db_path()
    conn = connect(db)
    conn.row_factory = sqlite3.Row
    # Listing is the other place a stale claim gets noticed, so retire the dead
    # ones before anyone reads the list and believes it.
    if sweep_expired(conn):
        conn.commit()
    where, params = [], []
    if args.active:
        where.append("status = 'active'")
    if args.by:
        where.append("agent = ?")
        params.append(args.by)
    if args.for_path:
        # naive overlap filter using path prefix; precise overlap is in cmd_claim
        where.append("(path LIKE ? OR ? LIKE path)")
        params.extend([f"{args.for_path}%", args.for_path])
    sql = "SELECT * FROM claims"
    if where:
        sql += " WHERE " + " AND ".join(where)
    sql += " ORDER BY id DESC LIMIT 50"
    rows = conn.execute(sql, params).fetchall()
    if not rows:
        print("(no claims match)")
        return 0
    for r in rows:
        wo = f" [{r['work_order']}]" if r["work_order"] else ""
        rel = f" released {short_time(r['released_at'])}" if r["released_at"] else ""
        exp = (
            f" expires {short_time(r['expires_at'])}"
            if r["status"] == "active" and r["expires_at"]
            else ""
        )
        print(
            f"#{r['id']} {r['status']:8} {r['agent']:7} "
            f"{r['path']}{wo} (claimed {short_time(r['claimed_at'])}){exp}{rel}"
        )
    return 0


def cmd_whoami(args: argparse.Namespace) -> int:
    require_known_agent(args.agent)
    role = ROLE_OF[args.agent]
    dept = DEPARTMENT_OF.get(args.agent, "-")
    chans = ", ".join(sorted(ACL[args.agent]))
    print(f"{args.agent}: {role} (dept: {dept}) channels: {chans}")
    return 0


def cmd_stats(_: argparse.Namespace) -> int:
    db = resolve_db_path()
    conn = connect(db)
    conn.row_factory = sqlite3.Row
    print(f"db: {db}")
    for ch in CHANNELS:
        total = conn.execute(
            "SELECT COUNT(*) AS c FROM messages WHERE channel = ?", (ch,)
        ).fetchone()["c"]
        print(f"  {ch}: {total} messages")
    active = conn.execute("SELECT COUNT(*) AS c FROM claims WHERE status = 'active'").fetchone()[
        "c"
    ]
    print(f"  active claims: {active}")
    return 0


def cmd_archive(args: argparse.Namespace) -> int:
    db = resolve_db_path()
    conn = connect(db)
    n = conn.execute("DELETE FROM messages WHERE posted_at < ?", (args.before,)).rowcount
    m = conn.execute("DELETE FROM audit WHERE at < ?", (args.before,)).rowcount
    conn.commit()
    print(f"archived {n} messages, {m} audit rows before {args.before}")
    return 0


def cmd_init(_: argparse.Namespace) -> int:
    db = resolve_db_path()
    connect(db).close()
    print(f"initialized {db}")
    return 0


# ---------------------------------------------------------------------------
# Path overlap (used by claim conflict detection AND by path_guard hook)
# ---------------------------------------------------------------------------


def _paths_overlap(a: str, b: str) -> bool:
    """Conservative overlap test for path globs.

    Treats either side as a glob; declares overlap if either matches the other
    or if their literal-prefix portions share a parent. Good enough for the
    coarse 'don't both edit packages/coa/**' use case.
    """
    if a == b:
        return True
    if fnmatch(a, b) or fnmatch(b, a):
        return True
    a_lit = a.split("*", 1)[0].rstrip("/")
    b_lit = b.split("*", 1)[0].rstrip("/")
    if not a_lit or not b_lit:
        return True
    return a_lit.startswith(b_lit) or b_lit.startswith(a_lit)


# ---------------------------------------------------------------------------
# Argparse wiring
# ---------------------------------------------------------------------------


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="comms", description=__doc__.split("\n", 1)[0])
    sub = p.add_subparsers(dest="cmd", required=True)

    sp = sub.add_parser("post", help="post a message to a channel")
    sp.add_argument("channel")
    sp.add_argument("from_agent")
    sp.add_argument("body", help="message body, or '-' to read from stdin")
    sp.add_argument("--to")
    sp.add_argument("--thread", type=int)
    sp.add_argument("--subject", required=True)
    sp.add_argument("--wo")
    sp.set_defaults(func=cmd_post)

    sp = sub.add_parser("read", help="read messages on a channel")
    sp.add_argument("channel")
    sp.add_argument("as_agent")
    sp.add_argument("--since", type=int)
    sp.add_argument("--unread", action="store_true")
    sp.add_argument(
        "--mine", action="store_true", help="only messages addressed to you or broadcast"
    )
    sp.add_argument("--limit", type=int, default=20)
    sp.add_argument("--verbose", "-v", action="store_true")
    sp.set_defaults(func=cmd_read)

    sp = sub.add_parser("thread", help="read a thread by root id")
    sp.add_argument("id", type=int)
    sp.add_argument("as_agent")
    sp.add_argument("--verbose", "-v", action="store_true")
    sp.set_defaults(func=cmd_thread)

    sp = sub.add_parser("inbox", help="messages addressed to you across allowed channels")
    sp.add_argument("as_agent")
    sp.add_argument("--unread", action="store_true")
    sp.add_argument("--limit", type=int, default=20)
    sp.set_defaults(func=cmd_inbox)

    sp = sub.add_parser("mark-read", help="advance your read cursor on a channel")
    sp.add_argument("channel")
    sp.add_argument("as_agent")
    sp.add_argument("--up-to", type=int)
    sp.set_defaults(func=cmd_mark_read)

    sp = sub.add_parser("claim", help="claim a path before editing it")
    sp.add_argument("path")
    sp.add_argument("as_agent")
    sp.add_argument("--wo")
    sp.add_argument(
        "--ttl",
        type=int,
        metavar="MINUTES",
        help=(
            f"claim lifetime in minutes (default {CLAIM_TTL_MINUTES}, or "
            "AGENT_ORG_CLAIM_TTL_MIN); 0 = never expires. Re-running `claim` on a "
            "path you already hold renews it."
        ),
    )
    sp.set_defaults(func=cmd_claim)

    sp = sub.add_parser("release", help="release a claim")
    g = sp.add_mutually_exclusive_group(required=True)
    g.add_argument("--path")
    g.add_argument("--id", type=int)
    sp.add_argument("as_agent")
    sp.set_defaults(func=cmd_release)

    sp = sub.add_parser("claims", help="list claims")
    sp.add_argument("--active", action="store_true")
    sp.add_argument("--by")
    sp.add_argument("--for-path")
    sp.set_defaults(func=cmd_claims)

    sp = sub.add_parser("whoami", help="show role + allowed channels for an agent")
    sp.add_argument("agent")
    sp.set_defaults(func=cmd_whoami)

    sp = sub.add_parser("stats", help="db stats")
    sp.set_defaults(func=cmd_stats)

    sp = sub.add_parser("archive", help="delete messages older than --before YYYY-MM-DD")
    sp.add_argument("--before", required=True)
    sp.set_defaults(func=cmd_archive)

    sp = sub.add_parser("init", help="force-initialize the db (otherwise lazy)")
    sp.set_defaults(func=cmd_init)

    return p


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
