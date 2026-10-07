-- Reviews move from a fixed ladder (3, 7, 21, 60, 180 days) to FSRS-6 (docs/SPACED_REPETITION.md): each problem
-- keeps a memory state, and the next due date comes from the model, snapped to the owner's review days.
-- `step` stays as a coarse 0..4 level derived from stability, so existing screens keep working.
ALTER TABLE reviews
    ADD COLUMN stability   real,
    ADD COLUMN difficulty  real,
    ADD COLUMN last_review timestamptz,
    ADD COLUMN last_grade  text CHECK (last_grade IN ('again', 'hard', 'good', 'easy')),
    ADD COLUMN reps        int NOT NULL DEFAULT 0,
    ADD COLUMN lapses      int NOT NULL DEFAULT 0;

-- Rows from the ladder: stability is the interval they were last given (by definition, the days until recall falls
-- to 90 %), difficulty starts at the model's middle, and an unassisted result counts as "good".
UPDATE reviews SET
    stability   = GREATEST(1.0, EXTRACT(epoch FROM (due_at - updated_at)) / 86400.0),
    difficulty  = 5.0,
    last_review = updated_at,
    last_grade  = CASE last_result WHEN 'unassisted' THEN 'good' ELSE 'hard' END,
    reps        = jsonb_array_length(history);

ALTER TABLE reviews
    ALTER COLUMN stability SET NOT NULL,
    ALTER COLUMN difficulty SET NOT NULL,
    ALTER COLUMN last_review SET NOT NULL,
    ALTER COLUMN last_grade SET NOT NULL;
