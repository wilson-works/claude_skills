"""agent-org PreToolUse path guard.

Enforces department ownership for Write / Edit / MultiEdit operations.

Logic:
  1. Read tool input from stdin (JSON, Claude Code hook contract).
  2. Resolve the target file path. If not a path-bearing tool, allow.
  3. Look up active comms claims overlapping the path.
       - unreadable -> NOT the same as "none". See UNREADABLE CLAIM STATE below.
       - 0 matches  -> assume main session or shared code, allow.
       - 1+ matches -> for each claiming agent, check their department's
         owned globs in org.config.json. Allow if any owning department
         claims the path OR the path is on the `shared` list.
       - Otherwise block, naming the conflicting agent + owning department.

UNREADABLE CLAIM STATE:
  "the claims table says nobody owns this" and "I could not read the claims
  table" are different facts with opposite safety meanings, and this hook used
  to collapse them into the same empty list. Under lock contention - precisely
  what concurrent lanes generate, and precisely when the guard matters most -
  that turned a SQLite busy error into an ALLOW. The read now retries, and a
  still-unreadable result takes its own branch (see STRICT_ON_UNREADABLE_CLAIMS).

Exit codes:
  0  allow
  2  block (Claude Code surfaces stderr)

Configure with:
  AGENT_ORG_DB        path to comms.db (defaults to <repo>/.claude/comms.db)
  AGENT_ORG_CONFIG    path to org.config.json (defaults to <repo>/.claude/agents/org.config.json)
  AGENT_ORG_DISABLE   set to 1 to short-circuit and always allow (debugging only)
  AGENT_ORG_GUARD_STRICT  set to 1 to fail CLOSED on unreadable claim state
"""

from __future__ import annotations

import json
import os
import sqlite3
import sys
import time
from fnmatch import fnmatch
from pathlib import Path

# Roster -> department. Mirrors comms.py intentionally; this hook is meant to
# be drop-in alongside comms.py, so the duplication keeps the hook standalone.
DEPARTMENT_OF: dict[str, str] = {
    # CTO branch — path_guard enforces path ownership for these agents
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
    # CFO + COO branches — advisory roles (Read/Grep/Glob/Bash + Agent for
    # heads). They do not get Edit/Write tools in their agent definitions, so
    # in practice path_guard never sees a claim from these agents. They are
    # listed here so that if an Edit ever reaches a path_guard check (e.g. via
    # the main session impersonating one of them), the agent is recognized and
    # the hook can render a clear "advisory-only" message rather than a vague
    # "unknown agent" trace. Department names are namespaced to avoid colliding
    # with CTO-branch department names.
    "hal": "cfo-controller",
    "lila": "cfo-controller",
    "theo": "cfo-controller",
    "imani": "cfo-treasury",
    "tomas": "cfo-treasury",
    "bea": "cfo-treasury",
    "anya": "cfo-tax",
    "reyna": "cfo-tax",
    "devon": "cfo-tax",
    "nadia": "cfo-fpa",
    "eli": "cfo-fpa",
    "quinn": "cfo-fpa",
    "roz": "coo-hr",
    "lena": "coo-hr",
    "chidi": "coo-hr",
    # CAO branch — Camille and Cole are write-capable under their dept globs;
    # Amelia, Victor, Clay, Wren are advisory (listed for clarity / message-rendering).
    "amelia": "cao-suite",
    "victor": "cao-suite",
    "elena": "cao-suite",
    "clay": "cao-claude",
    "camille": "copy",
    "cole": "coding-cao",
    "wren": "cao-wellness",
    # EA-rep branch — fully advisory (no Edit/Write tools); listed for messaging.
    "marisol": "ea-rep-suite",
    "anika": "ea-rep-suite",
    "otto": "ea-rep-exams",
    "tess": "ea-rep-exams",
    "kira": "ea-rep-collections",
    "rafa": "ea-rep-collections",
    "mateo": "ea-rep-notices",
    "ines": "ea-rep-notices",
    # CPA-attest branch — fully advisory (no Edit/Write tools); listed for messaging.
    "everett": "cpa-suite",
    "juno": "cpa-suite",
    "priscilla": "cpa-audit",
    "niall": "cpa-audit",
    "mason": "cpa-attest-other",
    "orla": "cpa-attest-other",
    "saira": "cpa-quality",
    "finn": "cpa-quality",
    # CMO branch — Rocco/Tate own demand/**, Yara/Luca own content/**;
    # Margot, Rina, Sela, Fern, Arlo, Iggy are advisory.
    "margot": "cmo-suite",
    "rina": "cmo-suite",
    "sela": "cmo-brand",
    "fern": "cmo-brand",
    "rocco": "demand",
    "tate": "demand",
    "yara": "content",
    "luca": "content",
    "arlo": "cmo-analytics",
    "iggy": "cmo-analytics",
}

PATH_TOOLS = {"Write", "Edit", "MultiEdit", "NotebookEdit"}

# ---------------------------------------------------------------------------
# Concurrency posture
# ---------------------------------------------------------------------------

# This hook is a SECOND PROCESS on the same SQLite file that comms.py writes.
# Much shorter than the comms.py CLI timeout (5000 ms) on purpose: this runs on
# the PreToolUse path of every Write/Edit, so its worst case is paid by a human
# waiting on a tool call.
#
# Budget the timeout at ~2x per attempt, not 1x: an attempt takes the busy
# timeout more than once (schema read, then query), so the wall clock is roughly
# 2 * BUSY_TIMEOUT_MS * READ_ATTEMPTS. MEASURED on this machine against a real
# second process holding BEGIN EXCLUSIVE: 3.57 / 3.60 / 3.60 s over three runs
# with the values below. The naive 1x arithmetic predicts 1.8 s and is wrong by
# 2x -- time it, do not derive it. The normal uncontended read is
# sub-millisecond and never retries.
BUSY_TIMEOUT_MS = 500
READ_ATTEMPTS = 3
RETRY_BACKOFF_S = 0.1  # doubles each attempt: 0.1 s, 0.2 s

# --- THE ENFORCEMENT SWITCH ------------------------------------------------
# False = OBSERVE-ONLY: on unreadable claim state, print a loud diagnostic and
#         ALLOW (exit 0). This is where we ship first, deliberately.
# True  = FAIL-CLOSED: same diagnostic, then BLOCK (exit 2).
#
# Flip this one line (or set AGENT_ORG_GUARD_STRICT=1 to try it without editing)
# ONLY after the calibration condition is met:
#
#   CALIBRATION CONDITION - one full multi-lane run (4 concurrent writers,
#   >= 2 h) produces ZERO "CLAIM STATE UNREADABLE" diagnostics in the hook
#   log. Non-zero means busy_timeout/retry are not yet absorbing real
#   contention, and flipping to fail-closed would block legitimate work at
#   exactly the moment the run is busiest. Fix the contention first.
STRICT_ON_UNREADABLE_CLAIMS = False


def find_repo_root(start: Path) -> Path:
    cur = start.resolve()
    for p in (cur, *cur.parents):
        if (p / ".git").exists():
            return p
    return start


def normalize(p: str) -> str:
    return p.replace("\\", "/")


def glob_match(path: str, pattern: str) -> bool:
    # fnmatch treats ** loosely; tighten with a simple ancestor check.
    if fnmatch(path, pattern):
        return True
    if "**" in pattern:
        prefix = pattern.split("**", 1)[0].rstrip("/")
        if prefix and path.startswith(prefix + "/"):
            return True
    return False


def paths_overlap(a: str, b: str) -> bool:
    if a == b or fnmatch(a, b) or fnmatch(b, a):
        return True
    a_lit = a.split("*", 1)[0].rstrip("/")
    b_lit = b.split("*", 1)[0].rstrip("/")
    if not a_lit or not b_lit:
        return True
    return a_lit.startswith(b_lit) or b_lit.startswith(a_lit)


def load_config(config_path: Path) -> dict:
    if not config_path.exists():
        return {}
    try:
        return json.loads(config_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        sys.stderr.write(f"[path_guard] org.config.json parse error: {exc}\n")
        return {}


def department_owns(config: dict, dept: str, rel_path: str) -> bool:
    deps = config.get("departments", {})
    spec = deps.get(dept)
    if not spec:
        return True  # unknown dept -> degraded: allow rather than misfire
    return any(glob_match(rel_path, normalize(pattern)) for pattern in spec.get("owns", []))


def is_shared(config: dict, rel_path: str) -> bool:
    return any(glob_match(rel_path, normalize(pattern)) for pattern in config.get("shared", []))


def active_claims_for(db_path: Path, rel_path: str) -> list[tuple[int, str, str]] | None:
    """Claims overlapping rel_path, or None if the claims table is UNREADABLE.

    The None return is the whole point: an empty list is a fact about ownership,
    None is the absence of any fact. Callers must not conflate them.
    """
    if not db_path.exists():
        return []  # no bus at all -> nothing has ever been claimed. A real fact.

    last_exc: Exception | None = None
    for attempt in range(READ_ATTEMPTS):
        conn = None
        try:
            conn = sqlite3.connect(str(db_path), timeout=BUSY_TIMEOUT_MS / 1000)
            conn.execute(f"PRAGMA busy_timeout = {BUSY_TIMEOUT_MS}")
            # An active claim past its expires_at is not an active claim. NULL
            # means "never expires" (every row written before comms.py grew the
            # column). comms.py does the actual sweep; the hook only reads.
            rows = conn.execute(
                "SELECT id, agent, path FROM claims WHERE status = 'active' "
                "AND (expires_at IS NULL "
                "     OR expires_at > strftime('%Y-%m-%dT%H:%M:%fZ', 'now'))"
            ).fetchall()
            return [
                (rid, agent, path) for rid, agent, path in rows if paths_overlap(rel_path, path)
            ]
        except sqlite3.OperationalError as exc:
            # "no such column: expires_at" -> a comms.db older than the schema
            # migration. Degrade to the pre-expiry query rather than reporting
            # the whole table unreadable.
            if "expires_at" in str(exc):
                try:
                    rows = conn.execute(
                        "SELECT id, agent, path FROM claims WHERE status = 'active'"
                    ).fetchall()
                    return [
                        (rid, agent, path)
                        for rid, agent, path in rows
                        if paths_overlap(rel_path, path)
                    ]
                except sqlite3.DatabaseError as inner:
                    last_exc = inner
            else:
                last_exc = exc
        except sqlite3.DatabaseError as exc:
            last_exc = exc
        finally:
            if conn is not None:
                try:
                    conn.close()
                except sqlite3.Error:
                    pass
        if attempt < READ_ATTEMPTS - 1:
            time.sleep(RETRY_BACKOFF_S * (2**attempt))

    sys.stderr.write(f"[path_guard] claims read failed after {READ_ATTEMPTS} attempts: {last_exc}\n")
    return None


def unreadable_claims(rel_path: str, db_path: Path) -> int:
    """Verdict for 'could not read the claims table'. Loud either way.

    Returns the hook exit code. Observe-only by default - see
    STRICT_ON_UNREADABLE_CLAIMS for the switch and its calibration condition.
    """
    strict = STRICT_ON_UNREADABLE_CLAIMS or os.environ.get("AGENT_ORG_GUARD_STRICT") == "1"
    verdict = "BLOCKED (strict)" if strict else "ALLOWED (observe-only)"
    sys.stderr.write(
        "[path_guard] *** CLAIM STATE UNREADABLE *** " + verdict + "\n"
        f"  target: {rel_path}\n"
        f"  db:     {db_path}\n"
        "  This is NOT 'no claims held'. Path ownership was NOT verified for\n"
        "  this write. Most likely cause: lock contention from concurrent lanes.\n"
        "  Set AGENT_ORG_GUARD_STRICT=1 (or flip STRICT_ON_UNREADABLE_CLAIMS in\n"
        "  this file) to fail closed once the calibration condition is met.\n"
    )
    return 2 if strict else 0


def main() -> int:
    if os.environ.get("AGENT_ORG_DISABLE") == "1":
        return 0

    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        return 0

    tool_name = payload.get("tool_name") or payload.get("name") or ""
    if tool_name not in PATH_TOOLS:
        return 0

    tool_input = payload.get("tool_input") or {}
    raw_path = (
        tool_input.get("file_path")
        or tool_input.get("notebook_path")
        or tool_input.get("path")
        or ""
    )
    if not raw_path:
        return 0

    repo_root = find_repo_root(Path.cwd())
    db_path = Path(os.environ.get("AGENT_ORG_DB") or repo_root / ".claude" / "comms.db")
    config_path = Path(
        os.environ.get("AGENT_ORG_CONFIG") or repo_root / ".claude" / "agents" / "org.config.json"
    )

    config = load_config(config_path)

    abs_path = Path(raw_path)
    if not abs_path.is_absolute():
        abs_path = (repo_root / abs_path).resolve()
    try:
        rel = normalize(str(abs_path.relative_to(repo_root)))
    except ValueError:
        # outside repo -> allow (out of scope for org enforcement)
        return 0

    claims = active_claims_for(db_path, rel)

    if claims is None:
        # UNREADABLE, not empty. Never fall through to the fail-open below.
        return unreadable_claims(rel, db_path)

    if not claims:
        # no claim held -> assume main session work; allow.
        return 0

    if is_shared(config, rel):
        return 0

    # Any claiming agent whose department owns this path => allow.
    for _cid, agent, _claim_path in claims:
        dept = DEPARTMENT_OF.get(agent)
        if not dept:
            # external agent claim -> allow (don't break unknown setups)
            return 0
        if department_owns(config, dept, rel):
            return 0

    # No claiming agent has authority over this path -> block.
    detail = ", ".join(
        f"{agent} ({DEPARTMENT_OF.get(agent, 'unknown')}) holds claim #{cid} on '{claim_path}'"
        for cid, agent, claim_path in claims
    )
    sys.stderr.write(
        "[path_guard] BLOCKED -- department mismatch.\n"
        f"  target: {rel}\n"
        f"  claims: {detail}\n"
        "  Hand this work off to the correct department head, or release the claim.\n"
    )
    return 2


if __name__ == "__main__":
    sys.exit(main())
