-- A run the CLI has started and not yet reported: the stage page shows "Running…" until the report arrives (or ten minutes pass).
CREATE TABLE course_run_starts (
    course     text        NOT NULL,
    stage_id   text        NOT NULL,
    started_at timestamptz NOT NULL DEFAULT now(),
    PRIMARY KEY (course, stage_id)
);
