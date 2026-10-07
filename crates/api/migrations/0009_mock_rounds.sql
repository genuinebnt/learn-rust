-- Finished mock interview rounds (docs/DSA.md, decision 25): the settings the round used, and how each problem went.
CREATE TABLE mock_rounds (
    id           bigserial   PRIMARY KEY,
    finished_at  timestamptz NOT NULL DEFAULT now(),
    config       jsonb       NOT NULL,
    items        jsonb       NOT NULL,
    seconds      integer     NOT NULL
);
CREATE INDEX mock_rounds_finished ON mock_rounds (finished_at DESC);
