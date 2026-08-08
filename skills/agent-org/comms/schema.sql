-- agent-org communication database
-- 22 channels with hard ACL separation, across seven branches plus one
-- cross-branch channel. comms.py holds the authoritative list (CHANNELS) and
-- the per-agent ACL; this header is a summary, not the source of truth:
--   CTO          c-suite, dept-heads, dev-floor
--   CFO          cfo-suite, cfo-dept-heads, finance-floor
--   COO          coo-suite, coo-dept-heads, ops-floor
--   CAO          cao-suite, cao-dept-heads, cao-floor
--   EA-rep       ea-rep-suite, ea-rep-dept-heads, ea-rep-floor
--   CPA-attest   cpa-suite, cpa-dept-heads, cpa-floor
--   CMO          cmo-suite, cmo-dept-heads, cmo-floor
--   cross-branch exec-eas
--
-- ACL is enforced in comms.py, not at the SQL layer. The DB just stores facts.

CREATE TABLE IF NOT EXISTS messages (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    channel     TEXT NOT NULL,
    from_agent  TEXT NOT NULL,
    to_agent    TEXT,
    thread_id   INTEGER REFERENCES messages(id),
    subject     TEXT NOT NULL,
    body        TEXT NOT NULL,
    work_order  TEXT,
    posted_at   TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now'))
);

CREATE INDEX IF NOT EXISTS idx_messages_channel_id ON messages(channel, id DESC);
CREATE INDEX IF NOT EXISTS idx_messages_thread     ON messages(thread_id);
CREATE INDEX IF NOT EXISTS idx_messages_to         ON messages(to_agent, id DESC);
CREATE INDEX IF NOT EXISTS idx_messages_wo         ON messages(work_order);

-- Per-agent read cursor so `read --unread` is cheap.
CREATE TABLE IF NOT EXISTS read_state (
    agent        TEXT NOT NULL,
    channel      TEXT NOT NULL,
    last_read_id INTEGER NOT NULL DEFAULT 0,
    PRIMARY KEY (agent, channel)
);

-- Path claims for conflict avoidance and the path_guard hook.
CREATE TABLE IF NOT EXISTS claims (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    path        TEXT NOT NULL,
    agent       TEXT NOT NULL,
    work_order  TEXT,
    claimed_at  TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
    released_at TEXT,
    -- Nullable on purpose. NULL means "never expires", which is what every row
    -- written before this column existed means. comms.py sets it on `claim`
    -- and sweeps active rows past it to status='expired'.
    expires_at  TEXT,
    status      TEXT NOT NULL DEFAULT 'active'
                CHECK (status IN ('active', 'released', 'expired'))
);

CREATE INDEX IF NOT EXISTS idx_claims_active ON claims(status, path);
CREATE INDEX IF NOT EXISTS idx_claims_agent  ON claims(agent, status);

-- At most one ACTIVE claim per exact path. This is the DB-level backstop for
-- the BEGIN IMMEDIATE transaction in comms.py cmd_claim: the transaction makes
-- the read-then-insert atomic, this index makes a lost race impossible even if
-- some future code path forgets the transaction. Partial, so released/expired
-- rows accumulate freely.
CREATE UNIQUE INDEX IF NOT EXISTS idx_claims_one_active_per_path
    ON claims(path) WHERE status = 'active';

-- Audit log for accountability (CTO / Chief Engineer can review who did what).
CREATE TABLE IF NOT EXISTS audit (
    id     INTEGER PRIMARY KEY AUTOINCREMENT,
    at     TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
    agent  TEXT NOT NULL,
    action TEXT NOT NULL,
    detail TEXT
);

CREATE INDEX IF NOT EXISTS idx_audit_agent ON audit(agent, id DESC);
