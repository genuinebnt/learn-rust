//! The review schedule, as pure functions. See docs/SPACED_REPETITION.md for the reasoning and the measurements.
//!
//! **The memory model is FSRS-6**, from the open-spaced-repetition project's official `fsrs` crate: the scheduler modern
//! Anki uses, fitted to hundreds of millions of reviews. Every problem has a stability (how many days until recall
//! drops to 90 %) and a difficulty; recall probability at any time is `retrievability`. Grading a review as
//! again / hard / good / easy updates both, and the model sets the next interval for the desired retention.
//!
//! **On top of it, the parts that fit this owner's routine** (all tested):
//! - every weekday has a capacity (how many reviews that day can take); due dates snap to days with room,
//!   preferring the day closest to the ideal one, a little early over late, and the lightest one;
//! - a problem's first review goes to the consolidation day (Sunday): the week's new problems are reviewed together;
//! - the plan for a day takes the most-forgotten problems first, up to that day's capacity ([`pick`]).

use chrono::{Datelike, Days, NaiveDate, Weekday};
use fsrs::{FSRS, FSRS6_DEFAULT_DECAY, MemoryState, current_retrievability};
use serde::{Deserialize, Serialize};

/// How a review went. Maps one to one onto FSRS's four ratings.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash, Serialize, Deserialize)]
#[serde(rename_all = "lowercase")]
pub enum Grade {
    /// Couldn't do it, or had to look.
    Again,
    /// Got there, but with real struggle or hints.
    Hard,
    /// Solved it on my own.
    Good,
    /// Instant: recalled the whole approach and wrote it without thinking.
    Easy,
}

impl Grade {
    pub fn as_str(self) -> &'static str {
        match self {
            Grade::Again => "again",
            Grade::Hard => "hard",
            Grade::Good => "good",
            Grade::Easy => "easy",
        }
    }

    pub fn parse(s: &str) -> Option<Grade> {
        Some(match s {
            "again" => Grade::Again,
            "hard" => Grade::Hard,
            "good" => Grade::Good,
            "easy" => Grade::Easy,
            _ => return None,
        })
    }

    /// The older two-value label kept in `reviews.last_result`.
    pub fn legacy_result(self) -> &'static str {
        match self {
            Grade::Good | Grade::Easy => "unassisted",
            Grade::Again | Grade::Hard => "assisted",
        }
    }
}

/// What the Rust workspace records on its own: a solve with no hints is "good", one that needed hints is "hard".
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum Outcome {
    Unassisted,
    Assisted,
}

impl Outcome {
    pub fn grade(self) -> Grade {
        match self {
            Outcome::Unassisted => Grade::Good,
            Outcome::Assisted => Grade::Hard,
        }
    }
}

/// How many reviews each weekday can take; 0 means no reviews that day.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
#[serde(default)]
pub struct Capacity {
    pub mon: u32,
    pub tue: u32,
    pub wed: u32,
    pub thu: u32,
    pub fri: u32,
    pub sat: u32,
    pub sun: u32,
}

impl Default for Capacity {
    /// One older problem a day on weekdays, a little practice on Saturday, and Sunday for the week's new problems plus
    /// a few older ones. No day takes more than 12: the plan is meant to never feel like a wall.
    fn default() -> Self {
        Capacity { mon: 1, tue: 1, wed: 1, thu: 1, fri: 1, sat: 3, sun: 12 }
    }
}

impl Capacity {
    pub fn on(&self, day: Weekday) -> u32 {
        match day {
            Weekday::Mon => self.mon,
            Weekday::Tue => self.tue,
            Weekday::Wed => self.wed,
            Weekday::Thu => self.thu,
            Weekday::Fri => self.fri,
            Weekday::Sat => self.sat,
            Weekday::Sun => self.sun,
        }
    }

    fn all(&self) -> [u32; 7] {
        [self.mon, self.tue, self.wed, self.thu, self.fri, self.sat, self.sun]
    }
}

/// The owner's knobs, saved under `settings.srs`.
#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(default)]
pub struct Settings {
    /// The recall probability FSRS aims for when it spaces reviews. Higher means more reviews.
    pub retention: f32,
    /// Reviews each weekday can take. The rest of a busy day rolls over to the next day with room.
    pub capacity: Capacity,
    /// The weekday (`mon` … `sun`) every problem's first review is held on, so a week's new problems are reviewed
    /// together. `None` lets the first review fall on any day with capacity.
    pub consolidate_on: Option<String>,
    /// New problems per day, for the pace tracker.
    pub new_per_day: u32,
    /// When the plan should be finished, e.g. the NeetCode 150.
    pub target_date: Option<NaiveDate>,
}

pub const MIN_RETENTION: f32 = 0.70;
pub const MAX_RETENTION: f32 = 0.97;

impl Default for Settings {
    fn default() -> Self {
        // The owner's routine: a new problem every day but Sunday; Sunday reviews the week's problems; one older
        // problem a day in between; the NeetCode 150 by the end of March.
        Settings { retention: 0.85, capacity: Capacity::default(), consolidate_on: Some("sun".into()), new_per_day: 1, target_date: NaiveDate::from_ymd_opt(2027, 3, 31) }
    }
}

impl Settings {
    pub fn validate(&self) -> Result<(), String> {
        if !(MIN_RETENTION..=MAX_RETENTION).contains(&self.retention) {
            return Err(format!("retention must be between {MIN_RETENTION} and {MAX_RETENTION}"));
        }
        if self.capacity.all().iter().all(|&c| c == 0) {
            return Err("give at least one weekday room for reviews".into());
        }
        if self.capacity.all().iter().any(|&c| c > 100) {
            return Err("a day can take at most 100 reviews".into());
        }
        if let Some(day) = &self.consolidate_on {
            let w = weekday(day).ok_or_else(|| format!("{day:?} isn't a weekday; use mon, tue, wed, thu, fri, sat or sun"))?;
            if self.capacity.on(w) == 0 {
                return Err(format!("{day} is the consolidation day but has no room for reviews"));
            }
        }
        if self.new_per_day > 20 {
            return Err("new problems per day must be 20 or fewer".into());
        }
        Ok(())
    }

    pub fn capacity_on(&self, day: NaiveDate) -> u32 {
        self.capacity.on(day.weekday())
    }

    fn consolidation_day(&self) -> Option<Weekday> {
        self.consolidate_on.as_deref().and_then(weekday)
    }
}

fn weekday(s: &str) -> Option<Weekday> {
    Some(match s {
        "mon" => Weekday::Mon,
        "tue" => Weekday::Tue,
        "wed" => Weekday::Wed,
        "thu" => Weekday::Thu,
        "fri" => Weekday::Fri,
        "sat" => Weekday::Sat,
        "sun" => Weekday::Sun,
        _ => return None,
    })
}

/// Probability of recalling the problem `elapsed_days` after its last review.
pub fn retrievability(memory: MemoryState, elapsed_days: f32) -> f32 {
    current_retrievability(memory, elapsed_days.max(0.0), FSRS6_DEFAULT_DECAY)
}

/// The readiness credit of a solved problem: its chance of being recalled, but never below a quarter of the credit,
/// since a problem you solved once is still worth something.
pub fn credit(memory: MemoryState, elapsed_days: f32) -> f64 {
    f64::from(retrievability(memory, elapsed_days)).max(0.25)
}

/// A coarse 0 to 4 level for display, from stability in days.
pub fn level(stability: f32) -> i32 {
    match stability {
        s if s < 3.0 => 0,
        s if s < 8.0 => 1,
        s if s < 21.0 => 2,
        s if s < 60.0 => 3,
        _ => GRADUATED,
    }
}

/// The level of a problem you know well: it has gone 60+ days without needing a review.
pub const GRADUATED: i32 = 4;

#[derive(Debug, Clone, Copy, PartialEq)]
pub struct Scheduled {
    pub memory: MemoryState,
    /// The interval FSRS asked for, in days.
    pub ideal_days: f32,
    /// The day the review is planned for, after snapping to review days.
    pub due: NaiveDate,
}

/// Schedules the next review.
///
/// `prev` is the memory state and the date of the last review, `None` for a first solve (whose next review is held
/// on the consolidation day). `load(day)` is how many reviews are already planned for `day`.
pub fn schedule(
    prev: Option<(MemoryState, NaiveDate)>,
    grade: Grade,
    today: NaiveDate,
    settings: &Settings,
    load: &dyn Fn(NaiveDate) -> u32,
) -> Result<Scheduled, String> {
    let elapsed = prev.map_or(0, |(_, last)| (today - last).num_days().max(0) as u32);
    let next = FSRS::default().next_states(prev.map(|(m, _)| m), settings.retention, elapsed).map_err(|e| e.to_string())?;
    let item = match grade {
        Grade::Again => next.again,
        Grade::Hard => next.hard,
        Grade::Good => next.good,
        Grade::Easy => next.easy,
    };
    let days = item.interval.round().max(1.0) as u64;
    let ideal = today + Days::new(days);
    let only = if prev.is_none() { settings.consolidation_day() } else { None };
    Ok(Scheduled { memory: item.memory, ideal_days: item.interval, due: snap(ideal, today, item.interval, settings, only, load) })
}

/// The day with room closest to `ideal`, within a window that grows with the interval. A day a little early costs
/// less than the same day late (a late review has forgotten more); a day's cost rises with the reviews already planned
/// for it, steeply once it's over its capacity. `only` limits the choice to one weekday.
fn snap(ideal: NaiveDate, today: NaiveDate, interval: f32, settings: &Settings, only: Option<Weekday>, load: &dyn Fn(NaiveDate) -> u32) -> NaiveDate {
    let span = f64::from(interval.max(1.0));
    let early = ((span * 0.25).floor() as u64).min(45);
    let late = ((span * 0.15).ceil() as u64).clamp(7, 45);
    let first = (ideal - Days::new(early)).max(today + Days::new(1));
    let last = ideal + Days::new(late);
    let mut best: Option<(f64, NaiveDate)> = None;
    let mut day = first;
    while day <= last {
        let cap = settings.capacity_on(day);
        if cap > 0 && only.is_none_or(|w| day.weekday() == w) {
            let delta = (day - ideal).num_days() as f64;
            let planned = f64::from(load(day));
            let over = (planned + 1.0 - f64::from(cap)).max(0.0);
            let cost = if delta < 0.0 { -delta / span } else { 1.5 * delta / span } + 0.04 * planned / f64::from(cap) + 0.3 * over;
            if best.is_none_or(|(c, _)| cost < c - 1e-9) {
                best = Some((cost, day));
            }
        }
        day = day + Days::new(1);
    }
    best.map_or(ideal, |(_, d)| d)
}

/// What one review day should hold: the problems due by `today`, most forgotten first, up to the day's capacity.
/// `cards` are `(id, memory, last review, due)`; the rest stay overdue and are first in line next time.
pub fn pick(today: NaiveDate, settings: &Settings, cards: &[(String, MemoryState, NaiveDate, NaiveDate)]) -> Vec<String> {
    let mut due: Vec<(f32, &str)> = cards
        .iter()
        .filter(|c| c.3 <= today)
        .map(|c| (retrievability(c.1, (today - c.2).num_days() as f32), c.0.as_str()))
        .collect();
    due.sort_by(|a, b| a.0.total_cmp(&b.0).then_with(|| a.1.cmp(b.1)));
    due.into_iter().take(settings.capacity_on(today) as usize).map(|(_, id)| id.to_owned()).collect()
}

#[cfg(test)]
mod tests {
    use super::*;

    fn d(s: &str) -> NaiveDate {
        s.parse().unwrap()
    }

    /// The owner's routine: one older review a weekday, 3 on Saturday, 12 on Sunday, first reviews held on Sunday.
    fn routine() -> Settings {
        Settings::default()
    }

    fn cap(mon: u32, tue: u32, wed: u32, thu: u32, fri: u32, sat: u32, sun: u32) -> Capacity {
        Capacity { mon, tue, wed, thu, fri, sat, sun }
    }

    fn sunday_only() -> Settings {
        Settings { capacity: cap(0, 0, 0, 0, 0, 0, 12), ..Settings::default() }
    }

    fn any_day() -> Settings {
        Settings { capacity: cap(5, 5, 5, 5, 5, 5, 5), consolidate_on: None, ..Settings::default() }
    }

    fn none(_: NaiveDate) -> u32 {
        0
    }

    /// First solves at 85 % desired retention, from the FSRS-6 default parameters (the numbers the probe in
    /// docs/SPACED_REPETITION.md printed). If a crate upgrade moves them, this test says so.
    #[test]
    fn first_solve_intervals_match_the_reference_model() {
        let next = FSRS::default().next_states(None, 0.85, 0).unwrap();
        let near = |got: f32, want: f32| assert!((got - want).abs() < 0.15, "got {got}, want {want}");
        near(next.again.interval, 0.4);
        near(next.hard.interval, 2.5);
        near(next.good.interval, 4.4);
        near(next.easy.interval, 15.8);
    }

    #[test]
    fn recall_at_the_ideal_interval_is_the_desired_retention() {
        for retention in [0.80f32, 0.85, 0.90] {
            let next = FSRS::default().next_states(None, retention, 0).unwrap();
            let r = retrievability(next.good.memory, next.good.interval);
            assert!((r - retention).abs() < 0.01, "retention {retention}: recall {r} at the ideal interval");
        }
    }

    #[test]
    fn better_grades_wait_longer_at_every_stage() {
        let f = FSRS::default();
        let mut state: Option<MemoryState> = None;
        let mut elapsed = 0;
        for _ in 0..6 {
            let n = f.next_states(state, 0.85, elapsed).unwrap();
            assert!(n.again.interval < n.hard.interval && n.hard.interval < n.good.interval && n.good.interval < n.easy.interval);
            state = Some(n.good.memory);
            elapsed = n.good.interval.round().max(1.0) as u32;
        }
    }

    #[test]
    fn a_lapse_shrinks_the_interval_sharply() {
        let f = FSRS::default();
        let mut state = None;
        let mut elapsed = 0;
        for _ in 0..4 {
            let n = f.next_states(state, 0.85, elapsed).unwrap();
            state = Some(n.good.memory);
            elapsed = n.good.interval.round() as u32;
        }
        let known = state.unwrap();
        let today = d("2027-03-01");
        let last = today - Days::new(u64::from(elapsed));
        let lapse = schedule(Some((known, last)), Grade::Again, today, &any_day(), &none).unwrap();
        // Forgetting something you knew for months doesn't reset it to day one, but it comes back far sooner than before.
        assert!(lapse.memory.stability < 0.25 * known.stability, "stability {} -> {}", known.stability, lapse.memory.stability);
        assert!(lapse.ideal_days < 0.25 * known.stability && lapse.ideal_days <= 45.0, "next interval {} days after knowing it for {}", lapse.ideal_days, known.stability);
        // A newer problem that's failed comes back within days.
        let fresh = schedule(None, Grade::Again, today, &any_day(), &none).unwrap();
        assert!(fresh.due <= today + Days::new(2), "a failed new problem is due {}", fresh.due);
    }

    #[test]
    fn reviewing_late_still_counts_and_earns_more_stability() {
        let f = FSRS::default();
        let first = f.next_states(None, 0.85, 0).unwrap().good;
        let on_time = f.next_states(Some(first.memory), 0.85, 4).unwrap().good.memory.stability;
        let late = f.next_states(Some(first.memory), 0.85, 12).unwrap().good.memory.stability;
        assert!(late > on_time, "remembering after a long gap is stronger evidence than on time");
    }

    #[test]
    fn a_problems_first_review_is_held_on_the_consolidation_day() {
        // Whichever day of the week a new problem is solved, its first review is a Sunday within two weeks: the week's
        // problems are reviewed together.
        for day in ["2026-10-05", "2026-10-06", "2026-10-07", "2026-10-08", "2026-10-09", "2026-10-10"] {
            for grade in [Grade::Again, Grade::Hard, Grade::Good, Grade::Easy] {
                let s = schedule(None, grade, d(day), &routine(), &none).unwrap();
                assert_eq!(s.due.weekday(), Weekday::Sun, "{grade:?} on {day} -> {}", s.due);
                assert!(s.due > d(day) && (s.due - d(day)).num_days() <= 21, "{grade:?} on {day} -> {}", s.due);
            }
        }
        // A midweek "good" is reviewed that Sunday, as FSRS wants (about 4 days).
        assert_eq!(schedule(None, Grade::Good, d("2026-10-07"), &routine(), &none).unwrap().due, d("2026-10-11"));
    }

    #[test]
    fn older_problems_come_back_on_any_day_with_room() {
        // After the first review, the next one isn't tied to Sunday: some land on weekdays.
        let mut today = d("2026-10-11");
        let mut prev: Option<(MemoryState, NaiveDate)> = Some((FSRS::default().next_states(None, 0.85, 0).unwrap().good.memory, d("2026-10-07")));
        let mut weekdays = 0;
        for grade in [Grade::Good, Grade::Good, Grade::Hard, Grade::Good, Grade::Good, Grade::Good, Grade::Good, Grade::Hard] {
            let s = schedule(prev, grade, today, &routine(), &none).unwrap();
            weekdays += usize::from(s.due.weekday() != Weekday::Sun);
            prev = Some((s.memory, today));
            today = s.due;
        }
        assert!(weekdays >= 3, "only {weekdays} of 8 later reviews were on weekdays");
    }

    #[test]
    fn a_full_day_pushes_the_review_to_a_neighbour_with_room() {
        let ideal = d("2026-12-09"); // a Wednesday, capacity 1
        let settings = routine();
        assert_eq!(snap(ideal, d("2026-10-07"), 60.0, &settings, None, &none), ideal, "with no load the ideal day wins");
        let busy = |day: NaiveDate| if day == ideal { 1 } else { 0 };
        let moved = snap(ideal, d("2026-10-07"), 60.0, &settings, None, &busy);
        assert_ne!(moved, ideal, "a full day isn't chosen when a neighbour is free");
        assert!((moved - ideal).num_days().abs() <= 3, "moved to {moved}");
        // A short interval has no room to move far: load can't pull a 4-day review a month away.
        let short = snap(d("2026-10-11"), d("2026-10-07"), 4.4, &settings, Some(Weekday::Sun), &|_| 100);
        assert!((short - d("2026-10-11")).num_days().abs() <= 8);
    }

    #[test]
    fn with_one_review_day_a_week_everything_lands_on_it() {
        let mut today = d("2026-10-07");
        let mut prev: Option<(MemoryState, NaiveDate)> = None;
        for grade in [Grade::Good, Grade::Good, Grade::Good, Grade::Hard, Grade::Good, Grade::Easy, Grade::Good] {
            let s = schedule(prev, grade, today, &sunday_only(), &none).unwrap();
            assert_eq!(s.due.weekday(), Weekday::Sun, "{} is a {}", s.due, s.due.weekday());
            prev = Some((s.memory, today));
            today = s.due;
        }
        // A failure comes back the next Sunday, however soon FSRS wanted it.
        assert_eq!(schedule(None, Grade::Again, d("2026-10-08"), &sunday_only(), &none).unwrap().due, d("2026-10-11"));
    }

    #[test]
    fn never_scheduled_in_the_past_or_today() {
        for grade in [Grade::Again, Grade::Hard, Grade::Good, Grade::Easy] {
            for today in ["2026-10-07", "2026-10-10", "2026-10-11"] {
                let s = schedule(None, grade, d(today), &routine(), &none).unwrap();
                assert!(s.due > d(today), "{grade:?} on {today} -> {}", s.due);
            }
        }
    }

    #[test]
    fn a_review_day_takes_the_most_forgotten_first_up_to_its_capacity() {
        let m = |days_known: f32| FSRS::default().next_states(None, 0.85, 0).unwrap().good.memory.stability * days_known;
        let mem = |stability: f32| MemoryState { stability: m(stability), difficulty: 5.0 };
        let cards = vec![
            ("fresh".to_owned(), mem(10.0), d("2026-10-30"), d("2026-11-10")),
            ("rusty".to_owned(), mem(1.0), d("2026-09-01"), d("2026-09-10")),
            ("so-so".to_owned(), mem(2.0), d("2026-10-01"), d("2026-10-20")),
            ("not due".to_owned(), mem(5.0), d("2026-11-01"), d("2026-12-25")),
        ];
        let settings = routine();
        // A Wednesday has room for one: the most forgotten of those due.
        assert_eq!(pick(d("2026-11-11"), &settings, &cards), ["rusty"]);
        // A Sunday has room for them all (but not what isn't due), most forgotten first.
        assert_eq!(pick(d("2026-11-15"), &settings, &cards), ["rusty", "so-so", "fresh"]);
        // A day with no capacity holds nothing, and nothing is dropped: it's still due next time.
        let closed = Settings { capacity: cap(0, 0, 0, 0, 0, 0, 12), consolidate_on: None, ..settings };
        assert!(pick(d("2026-11-11"), &closed, &cards).is_empty());
        assert_eq!(pick(d("2026-11-15"), &closed, &cards).len(), 3);
    }

    #[test]
    fn settings_are_validated() {
        assert!(Settings::default().validate().is_ok());
        assert!(Settings { retention: 0.5, ..Settings::default() }.validate().is_err());
        assert!(Settings { retention: 0.99, ..Settings::default() }.validate().is_err());
        assert!(Settings { capacity: cap(0, 0, 0, 0, 0, 0, 0), consolidate_on: None, ..Settings::default() }.validate().is_err());
        assert!(Settings { capacity: cap(0, 0, 0, 0, 0, 0, 500), ..Settings::default() }.validate().is_err());
        assert!(Settings { consolidate_on: Some("funday".into()), ..Settings::default() }.validate().is_err());
        assert!(Settings { capacity: cap(1, 1, 1, 1, 1, 1, 0), ..Settings::default() }.validate().is_err(), "Sunday is the consolidation day but has no room");
        assert!(Settings { new_per_day: 99, ..Settings::default() }.validate().is_err());
        // Settings saved before a field existed still load, with the owner's routine for the rest.
        let s: Settings = serde_json::from_str(r#"{ "retention": 0.9 }"#).unwrap();
        assert_eq!((s.capacity, s.consolidate_on.as_deref()), (Capacity::default(), Some("sun")));
        let s: Settings = serde_json::from_str(r#"{ "capacity": { "sun": 20 } }"#).unwrap();
        assert_eq!((s.capacity.sun, s.capacity.sat, s.capacity.mon), (20, 3, 1));
    }

    #[test]
    fn credit_never_falls_below_a_quarter() {
        let m = FSRS::default().next_states(None, 0.85, 0).unwrap().good.memory;
        assert!(credit(m, 0.0) > 0.99);
        // The forgetting curve has a long tail (about a third after 5,000 days), so the floor only matters far out.
        assert!(credit(m, 5000.0) > 0.25 && credit(m, 5000.0) < credit(m, 100.0));
        assert_eq!(credit(m, 1.0e9), 0.25);
        assert!(level(1.0) == 0 && level(5.0) == 1 && level(15.0) == 2 && level(40.0) == 3 && level(400.0) == GRADUATED);
    }

    /// The battle test: a simulated learner whose recall follows the model's own forgetting curve, living the owner's
    /// routine for 175 days: a new problem Monday to Saturday (143 of them), reviews planned by `schedule` and done as
    /// `pick` says. The share of reviews that succeed should be close to the desired retention (a little under, since
    /// capacity makes some reviews late), and no problem is ever lost: every one keeps a future due date.
    #[test]
    fn simulated_learner_recalls_about_as_often_as_promised() {
        struct Rng(u64);
        impl Rng {
            fn next(&mut self) -> f32 {
                self.0 ^= self.0 << 13;
                self.0 ^= self.0 >> 7;
                self.0 ^= self.0 << 17;
                (self.0 >> 40) as f32 / (1u64 << 24) as f32
            }
        }
        let settings = routine();
        let start = d("2026-10-07");
        let mut rng = Rng(0x9E3779B97F4A7C15);
        let mut cards: Vec<(String, MemoryState, NaiveDate, NaiveDate)> = Vec::new();
        let (mut ok, mut tries, mut busiest) = (0u32, 0u32, 0usize);
        for offset in 0..175u64 {
            let today = start + Days::new(offset);
            let load_of = |cards: &Vec<(String, MemoryState, NaiveDate, NaiveDate)>, day: NaiveDate| cards.iter().filter(|c| c.3 == day).count() as u32;
            if cards.len() < 143 && today.weekday() != Weekday::Sun {
                let grade = if rng.next() < 0.1 { Grade::Again } else if rng.next() < 0.25 { Grade::Hard } else { Grade::Good };
                let s = schedule(None, grade, today, &settings, &|day| load_of(&cards, day)).unwrap();
                cards.push((cards.len().to_string(), s.memory, today, s.due));
            }
            let todo = pick(today, &settings, &cards);
            assert!(todo.len() <= settings.capacity_on(today) as usize, "{today}: {} reviews", todo.len());
            busiest = busiest.max(todo.len());
            for id in todo {
                let i: usize = id.parse().unwrap();
                let r = retrievability(cards[i].1, (today - cards[i].2).num_days() as f32);
                let recalled = rng.next() < r;
                tries += 1;
                ok += u32::from(recalled);
                let grade = if !recalled { Grade::Again } else if rng.next() < 0.15 { Grade::Hard } else { Grade::Good };
                let s = schedule(Some((cards[i].1, cards[i].2)), grade, today, &settings, &|day| load_of(&cards, day)).unwrap();
                cards[i] = (id, s.memory, today, s.due);
            }
        }
        let rate = f64::from(ok) / f64::from(tries);
        assert!(tries > 400, "only {tries} reviews happened");
        assert!((0.78..=0.92).contains(&rate), "recall at review was {rate:.3}, wanted about 0.85");
        assert!(busiest <= 12, "a day held {busiest} reviews");
        assert!(cards.iter().all(|c| c.3 > start), "every problem has a future due date");
    }
}
