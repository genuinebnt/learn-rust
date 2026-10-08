-- LeetCode's statement and hints for a problem, fetched once and kept (docs/DSA.md, decision 5).
CREATE TABLE dsa_statements (
    slug        text        PRIMARY KEY,
    html        text,
    hints       jsonb       NOT NULL DEFAULT '[]',
    locked      boolean     NOT NULL DEFAULT false,
    fetched_at  timestamptz NOT NULL DEFAULT now()
);
