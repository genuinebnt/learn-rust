-- Courses (courses/<id>): the owner's progress through each stage, every test run reported by the CLI, and the
-- stage solutions the CLI uploaded (they are not in the public repo; only the signed-in owner can read them).
CREATE TABLE course_stage_state (
    course            text        NOT NULL,
    stage_id          text        NOT NULL,
    hints_revealed    integer     NOT NULL DEFAULT 0,
    solution_revealed boolean     NOT NULL DEFAULT false,
    solved_at         timestamptz,
    -- A hint or the solution was opened before the stage first passed.
    assisted          boolean     NOT NULL DEFAULT false,
    PRIMARY KEY (course, stage_id)
);

CREATE TABLE course_runs (
    id          bigserial   PRIMARY KEY,
    course      text        NOT NULL,
    stage_id    text        NOT NULL,
    ok          boolean     NOT NULL,
    passed      integer     NOT NULL,
    total       integer     NOT NULL,
    tests       jsonb       NOT NULL DEFAULT '[]',
    problem     text,
    commit_sha  text,
    duration_ms integer     NOT NULL DEFAULT 0,
    at          timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX course_runs_stage ON course_runs (course, stage_id, at DESC);

CREATE TABLE course_solutions (
    course     text        NOT NULL,
    stage_id   text        NOT NULL,
    -- Unified-diff lines (' ', '+', '-' prefixes) per file, as JSON: [{"path": "...", "lines": ["+..."]}]
    files      jsonb       NOT NULL,
    updated_at timestamptz NOT NULL DEFAULT now(),
    PRIMARY KEY (course, stage_id)
);
