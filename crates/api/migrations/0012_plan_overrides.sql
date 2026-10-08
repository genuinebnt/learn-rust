-- The owner's changes to the calendar: a date made a problem day, a practice day or a break, per saved plan
-- (docs/DSA.md, decision 28). Everything else about the plan is worked out from these and the plan's rules.
CREATE TABLE plan_overrides (
    plan_id text NOT NULL,
    day     date NOT NULL,
    kind    text NOT NULL CHECK (kind IN ('solve', 'practice', 'break')),
    PRIMARY KEY (plan_id, day)
);
