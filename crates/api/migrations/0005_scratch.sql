-- The scratch `main.rs` per problem ("Run" builds it against your lib.rs and runs it).
CREATE TABLE scratch (
    problem_id  text        PRIMARY KEY,
    code        text        NOT NULL,
    updated_at  timestamptz NOT NULL DEFAULT now()
);
