CREATE TABLE profiles (
    profile_id TEXT PRIMARY KEY,
    handle TEXT NOT NULL,
    display_name TEXT NOT NULL,
    observed_at TEXT NOT NULL,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE UNIQUE INDEX idx_profiles_handle_nocase ON profiles(handle COLLATE NOCASE);

CREATE TABLE posts (
    post_id TEXT PRIMARY KEY,
    author_profile_id TEXT NOT NULL REFERENCES profiles(profile_id),
    canonical_url TEXT NOT NULL UNIQUE,
    text TEXT NOT NULL,
    published_at TEXT NOT NULL,
    post_type TEXT NOT NULL
);

CREATE INDEX idx_posts_author_published ON posts(author_profile_id, published_at);

CREATE TABLE media_assets (
    asset_id TEXT PRIMARY KEY,
    post_id TEXT NOT NULL REFERENCES posts(post_id),
    media_index INTEGER NOT NULL CHECK (media_index >= 0),
    media_type TEXT NOT NULL,
    duration_ms INTEGER CHECK (duration_ms IS NULL OR duration_ms >= 0),
    width INTEGER CHECK (width IS NULL OR width >= 0),
    height INTEGER CHECK (height IS NULL OR height >= 0),
    variants_json TEXT NOT NULL,
    UNIQUE(post_id, media_index)
);

CREATE TABLE discovery_runs (
    run_id TEXT PRIMARY KEY,
    strategy TEXT NOT NULL,
    started_at TEXT NOT NULL,
    finished_at TEXT,
    cursor TEXT,
    discovered_count INTEGER NOT NULL CHECK (discovered_count >= 0),
    error_count INTEGER NOT NULL CHECK (error_count >= 0),
    status TEXT NOT NULL
);

CREATE TABLE download_jobs (
    job_id TEXT PRIMARY KEY,
    asset_id TEXT NOT NULL REFERENCES media_assets(asset_id),
    run_id TEXT NOT NULL REFERENCES discovery_runs(run_id),
    status TEXT NOT NULL,
    attempts INTEGER NOT NULL CHECK (attempts >= 0),
    error_code TEXT,
    error_message TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE INDEX idx_download_jobs_status ON download_jobs(status);
CREATE INDEX idx_download_jobs_run ON download_jobs(run_id);

CREATE TABLE artifacts (
    artifact_id TEXT PRIMARY KEY,
    job_id TEXT NOT NULL REFERENCES download_jobs(job_id),
    relative_path TEXT NOT NULL UNIQUE,
    mime_type TEXT NOT NULL,
    size_bytes INTEGER NOT NULL CHECK (size_bytes >= 0),
    sha256 TEXT NOT NULL CHECK (length(sha256) = 64),
    created_at TEXT NOT NULL
);

CREATE INDEX idx_artifacts_job ON artifacts(job_id);
