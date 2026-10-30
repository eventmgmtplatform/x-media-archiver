CREATE TABLE archive_runs_v3 (
    run_id TEXT PRIMARY KEY,
    target_handle TEXT NOT NULL,
    requested_total INTEGER NOT NULL CHECK (requested_total >= 1),
    batch_size INTEGER NOT NULL CHECK (batch_size BETWEEN 1 AND 20),
    request_interval_seconds INTEGER NOT NULL CHECK (request_interval_seconds BETWEEN 1 AND 60),
    status TEXT NOT NULL CHECK (status IN ('PENDING','RUNNING','PAUSED','COMPLETED','FAILED')),
    existing_before INTEGER NOT NULL CHECK (existing_before >= 0),
    downloaded_total INTEGER NOT NULL CHECK (downloaded_total >= 0),
    page_number INTEGER NOT NULL CHECK (page_number >= 0),
    checkpoint_strategy TEXT NOT NULL,
    last_error_code TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    completed_at TEXT,
    archive_mode TEXT NOT NULL DEFAULT 'BOUNDED' CHECK (archive_mode IN ('BOUNDED','ALL')),
    completion_reason TEXT,
    failed_total INTEGER NOT NULL DEFAULT 0 CHECK (failed_total >= 0),
    max_items INTEGER,
    max_runtime_seconds INTEGER NOT NULL DEFAULT 3600,
    min_free_space_bytes INTEGER NOT NULL DEFAULT 10737418240,
    resumed_at TEXT
);

CREATE TABLE archive_checkpoints_v3 (
    run_id TEXT PRIMARY KEY REFERENCES archive_runs_v3(run_id) ON DELETE CASCADE,
    known_identity_count INTEGER NOT NULL CHECK (known_identity_count >= 0),
    last_completed_page INTEGER NOT NULL CHECK (last_completed_page >= 0),
    next_allowed_at TEXT,
    updated_at TEXT NOT NULL
);

INSERT INTO archive_runs_v3 (
    run_id,target_handle,requested_total,batch_size,request_interval_seconds,status,
    existing_before,downloaded_total,page_number,checkpoint_strategy,last_error_code,
    created_at,updated_at,completed_at
) SELECT run_id,target_handle,requested_total,batch_size,request_interval_seconds,status,
    existing_before,downloaded_total,page_number,checkpoint_strategy,last_error_code,
    created_at,updated_at,completed_at FROM archive_runs;

INSERT INTO archive_checkpoints_v3
SELECT run_id,known_identity_count,last_completed_page,next_allowed_at,updated_at
FROM archive_checkpoints;

DROP TABLE archive_checkpoints;
DROP TABLE archive_runs;
ALTER TABLE archive_runs_v3 RENAME TO archive_runs;
ALTER TABLE archive_checkpoints_v3 RENAME TO archive_checkpoints;
