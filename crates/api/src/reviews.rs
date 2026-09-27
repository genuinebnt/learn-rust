//! The review schedule (PLAN.md, learning rules), as pure functions.
//!
//! An assisted solve comes back in 3 days. Each unassisted re-solve moves a problem up the ladder
//! 3 → 7 → 21 → 60 days, then it graduates; an assisted re-solve sends it back to 3. An unassisted
//! first solve gets one retention check at 21 days. Overdue reviews cost readiness 10 % a week.

use chrono::{DateTime, TimeDelta, Utc};

/// Days until the next review at each step.
pub const LADDER: [i64; 4] = [3, 7, 21, 60];
/// The step after passing the 60-day review.
pub const GRADUATED: i32 = 4;
/// Graduated problems still come back, rarely.
const GRADUATED_DAYS: i64 = 180;

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum Outcome {
    Unassisted,
    Assisted,
}

impl Outcome {
    pub fn as_str(self) -> &'static str {
        match self {
            Outcome::Unassisted => "unassisted",
            Outcome::Assisted => "assisted",
        }
    }
}

/// The step and days until due after a solve. `prev` is the step before, `None` for a first solve.
pub fn next(prev: Option<i32>, outcome: Outcome) -> (i32, i64) {
    match (prev, outcome) {
        (_, Outcome::Assisted) => (0, LADDER[0]),
        (None, Outcome::Unassisted) => (2, LADDER[2]),
        (Some(s), Outcome::Unassisted) if s >= 3 => (GRADUATED, GRADUATED_DAYS),
        (Some(s), Outcome::Unassisted) => {
            let step = (s + 1).max(0);
            (step, LADDER[step as usize])
        }
    }
}

/// Readiness credit multiplier: 1 until due, then 10 % less per overdue week, never below 0.25.
pub fn decay(due_at: DateTime<Utc>, now: DateTime<Utc>) -> f64 {
    let overdue = now - due_at;
    if overdue <= TimeDelta::zero() {
        return 1.0;
    }
    let weeks = overdue.num_days() as f64 / 7.0;
    (1.0 - 0.1 * weeks).max(0.25)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn first_solves() {
        assert_eq!(next(None, Outcome::Assisted), (0, 3));
        assert_eq!(next(None, Outcome::Unassisted), (2, 21), "one retention check");
    }

    #[test]
    fn climbing_and_resetting() {
        assert_eq!(next(Some(0), Outcome::Unassisted), (1, 7));
        assert_eq!(next(Some(1), Outcome::Unassisted), (2, 21));
        assert_eq!(next(Some(2), Outcome::Unassisted), (3, 60));
        assert_eq!(next(Some(3), Outcome::Unassisted), (GRADUATED, 180));
        assert_eq!(next(Some(GRADUATED), Outcome::Unassisted), (GRADUATED, 180));
        assert_eq!(next(Some(3), Outcome::Assisted), (0, 3), "an assisted re-solve resets");
    }

    #[test]
    fn decay_is_ten_percent_a_week_with_a_floor() {
        let due: DateTime<Utc> = "2026-09-01T00:00:00Z".parse().unwrap();
        let at = |days: i64| due + TimeDelta::days(days);
        assert_eq!(decay(due, at(-3)), 1.0);
        assert_eq!(decay(due, at(0)), 1.0);
        assert!((decay(due, at(14)) - 0.8).abs() < 1e-9);
        assert_eq!(decay(due, at(365)), 0.25);
    }
}
