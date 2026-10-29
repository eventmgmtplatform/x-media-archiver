CREATE TABLE archive_runs (
    run_id TEXT PRIMARY KEY,
    target_handle TEXT NOT NULL,
    requested_total INTEGER NOT NULL CHECK (requested_total BETWEEN 1 AND 10),
    batch_size INTEGER NOT NULL CHECK (batch_size BETWEEN 1 AND 5),
    request_interval_seconds INTEGER NOT NULL CHECK (request_interval_seconds BETWEEN 1 AND 60),
    status TEXT NOT NULL CHECK (status IN ('PENDING','RUNNING','PAUSED','COMPLETED','FAILED')),
    existing_before INTEGER NOT NULL CHECK (existing_before >= 0),
    downloaded_total INTEGER NOT NULL CHECK (downloaded_total >= 0),
    page_number INTEGER NOT NULL CHECK (page_number >= 0),
    checkpoint_strategy TEXT NOT NULL,
    last_error_code TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    completed_at TEXT
);

CREATE TABLE archive_checkpoints (
    run_id TEXT PRIMARY KEY REFERENCES archive_runs(run_id) ON DELETE CASCADE,
    known_identity_count INTEGER NOT NULL CHECK (known_identity_count >= 0),
    last_completed_page INTEGER NOT NULL CHECK (last_completed_page >= 0),
    next_allowed_at TEXT,
    updated_at TEXT NOT NULL
);
