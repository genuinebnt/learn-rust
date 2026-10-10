-- The repository (on GitHub or elsewhere) that holds the learner's own work for a course, so `anneal course restore` on a new laptop can find it.
CREATE TABLE course_repos (
    course     text        PRIMARY KEY,
    url        text        NOT NULL,
    updated_at timestamptz NOT NULL DEFAULT now()
);
