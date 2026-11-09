-- 1. DOMAIN TABLES (Runs and Sub-tasks)
CREATE TABLE IF NOT EXISTS RUN (
    run_id INTEGER PRIMARY KEY AUTOINCREMENT,
    task TEXT NOT NULL,
    budget_level TEXT,
    cap DECIMAL NOT NULL,
    status TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS SUB_TASK (
    subtask_id INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id INTEGER NOT NULL,
    position INTEGER,
    description TEXT NOT NULL,
    status TEXT NOT NULL,
    FOREIGN KEY(run_id) REFERENCES RUN(run_id)
);

CREATE TABLE IF NOT EXISTS SUB_TASK_DEPENDENCY (
    subtask_id INTEGER NOT NULL,
    depends_on_id INTEGER NOT NULL,
    PRIMARY KEY (subtask_id, depends_on_id),
    FOREIGN KEY(subtask_id) REFERENCES SUB_TASK(subtask_id),
    FOREIGN KEY(depends_on_id) REFERENCES SUB_TASK(subtask_id)
);

-- 2. REGISTRY TABLES (Models, Pricing, and Quality)
CREATE TABLE IF NOT EXISTS MODEL (
    model_id INTEGER PRIMARY KEY AUTOINCREMENT,
    identifier TEXT NOT NULL UNIQUE,
    provider TEXT NOT NULL,
    stage TEXT NOT NULL,
    enabled BOOLEAN NOT NULL DEFAULT 1
);

CREATE TABLE IF NOT EXISTS PRICE_HISTORY (
    price_id INTEGER PRIMARY KEY AUTOINCREMENT,
    model_id INTEGER NOT NULL,
    input_price DECIMAL NOT NULL,
    output_price DECIMAL NOT NULL,
    effective_from DATE NOT NULL,
    FOREIGN KEY(model_id) REFERENCES MODEL(model_id)
);

CREATE TABLE IF NOT EXISTS QUALITY_SCORE (
    score_id INTEGER PRIMARY KEY AUTOINCREMENT,
    model_id INTEGER NOT NULL,
    task_type TEXT NOT NULL,
    score DECIMAL NOT NULL,
    measured_on DATE NOT NULL,
    FOREIGN KEY(model_id) REFERENCES MODEL(model_id)
);

-- 3. THE LEDGER (Strictly Append-Only)
CREATE TABLE IF NOT EXISTS LEDGER (
    ledger_id INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id INTEGER NOT NULL,
    subtask_id INTEGER,
    model_id INTEGER NOT NULL,
    attempt INTEGER NOT NULL,
    est_cost DECIMAL NOT NULL,
    actual_cost DECIMAL,
    tokens_in INTEGER,
    tokens_out INTEGER,
    input_price DECIMAL NOT NULL,
    output_price DECIMAL NOT NULL,
    decision TEXT NOT NULL,
    reason TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(run_id) REFERENCES RUN(run_id),
    FOREIGN KEY(subtask_id) REFERENCES SUB_TASK(subtask_id),
    FOREIGN KEY(model_id) REFERENCES MODEL(model_id)
);

-- 4. CACHE AND AUDIT
CREATE TABLE IF NOT EXISTS RESPONSE_CACHE (
    cache_id INTEGER PRIMARY KEY AUTOINCREMENT,
    ledger_id INTEGER NOT NULL,
    response TEXT NOT NULL,
    FOREIGN KEY(ledger_id) REFERENCES LEDGER(ledger_id)
);

CREATE TABLE IF NOT EXISTS AUDIT_LOG (
    audit_id INTEGER PRIMARY KEY AUTOINCREMENT,
    action TEXT NOT NULL,
    entity TEXT NOT NULL,
    before_value TEXT,
    after_value TEXT,
    changed_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 5. NFR3 TRIGGERS: Enforce Append-Only Ledger
CREATE TRIGGER IF NOT EXISTS prevent_ledger_update
BEFORE UPDATE ON LEDGER
BEGIN
    SELECT RAISE(ABORT, 'Auditability Violation (NFR3): Updates to the LEDGER table are strictly prohibited.');
END;

CREATE TRIGGER IF NOT EXISTS prevent_ledger_delete
BEFORE DELETE ON LEDGER
BEGIN
    SELECT RAISE(ABORT, 'Auditability Violation (NFR3): Deletions from the LEDGER table are strictly prohibited.');
END;