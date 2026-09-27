-- Browser sessions for the single user. Only a SHA-256 of each token is stored,
-- so a database leak doesn't hand out live sessions.
CREATE TABLE sessions (
    token_hash  bytea       PRIMARY KEY,
    created_at  timestamptz NOT NULL DEFAULT now(),
    expires_at  timestamptz NOT NULL
);

-- User settings, one JSON document per key, e.g. 'editor' → {"font_size": 13, "font_family": "JetBrains Mono"}.
CREATE TABLE settings (
    key         text        PRIMARY KEY,
    value       jsonb       NOT NULL,
    updated_at  timestamptz NOT NULL DEFAULT now()
);
