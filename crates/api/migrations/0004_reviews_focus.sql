-- Spaced repetition: one row per problem once it has been solved (PLAN.md learning rules).
-- step 0–3 is the 3/7/21/60-day ladder; 4 means graduated (checked again after 180 days).
CREATE TABLE reviews (
    problem_id  text        PRIMARY KEY,
    step        int         NOT NULL CHECK (step BETWEEN 0 AND 4),
    due_at      timestamptz NOT NULL,
    last_result text        NOT NULL CHECK (last_result IN ('unassisted', 'assisted')),
    -- [{"at": ..., "result": "unassisted", "resolve": true, "step": 2}, ...]
    history     jsonb       NOT NULL DEFAULT '[]',
    updated_at  timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX reviews_due ON reviews (due_at);

-- Seconds of active editing per problem per local day, from the workspace heartbeat.
CREATE TABLE focus_time (
    day         date        NOT NULL,
    problem_id  text        NOT NULL,
    seconds     int         NOT NULL CHECK (seconds >= 0),
    PRIMARY KEY (day, problem_id)
);
