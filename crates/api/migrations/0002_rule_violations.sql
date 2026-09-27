-- Fix-this rule breaks found before a run, e.g. [{"rule": "clone", "message": "...", "line": 13}].
-- A submit with any violation doesn't solve the problem, even if every test passes.
ALTER TABLE runs ADD COLUMN violations jsonb NOT NULL DEFAULT '[]';
