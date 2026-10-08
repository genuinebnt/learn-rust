-- The owner's own solutions to DSA problems, kept so they can be read later. A problem can have any number.
CREATE TABLE dsa_solutions (
    id          bigserial   PRIMARY KEY,
    problem_id  text        NOT NULL,
    label       text        NOT NULL DEFAULT '',
    code        text        NOT NULL,
    notes       text        NOT NULL DEFAULT '',
    created_at  timestamptz NOT NULL DEFAULT now(),
    updated_at  timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX dsa_solutions_problem ON dsa_solutions (problem_id, created_at);
