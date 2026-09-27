-- One row per attempt at a problem. A re-solve starts a new attempt.
CREATE TABLE attempts (
    id                bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    problem_id        text        NOT NULL,
    kind              text        NOT NULL DEFAULT 'practice' CHECK (kind IN ('practice', 'resolve', 'mock')),
    started_at        timestamptz NOT NULL DEFAULT now(),
    solved_at         timestamptz,
    hints_revealed    int         NOT NULL DEFAULT 0 CHECK (hints_revealed >= 0),
    solution_revealed boolean     NOT NULL DEFAULT false,
    -- Set by any hint or an early solution reveal. Assisted solves count half.
    assisted          boolean     NOT NULL DEFAULT false
);
CREATE INDEX attempts_by_problem ON attempts (problem_id, started_at DESC);

-- Every Run and Submit, with the code that was run, for the timeline and diffs.
CREATE TABLE runs (
    id          bigint      GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    attempt_id  bigint      NOT NULL REFERENCES attempts (id) ON DELETE CASCADE,
    problem_id  text        NOT NULL,
    kind        text        NOT NULL CHECK (kind IN ('run', 'submit')),
    code        text        NOT NULL,
    status      text        NOT NULL,
    passed      int         NOT NULL,
    total       int         NOT NULL,
    result      jsonb       NOT NULL,
    created_at  timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX runs_by_attempt ON runs (attempt_id, id);

-- The editor buffer, autosaved.
CREATE TABLE drafts (
    problem_id  text        PRIMARY KEY,
    code        text        NOT NULL,
    updated_at  timestamptz NOT NULL DEFAULT now()
);
