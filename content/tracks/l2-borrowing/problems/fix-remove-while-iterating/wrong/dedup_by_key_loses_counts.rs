#[derive(Debug, PartialEq)]
pub struct Event {
    pub key: String,
    pub count: u32,
}

/// Merges each run of adjacent events with the same key into the run's first event, adding up the counts.
/// Returns how many events were removed.
pub fn merge_runs(events: &mut Vec<Event>) -> usize {
    let before = events.len();
    events.dedup_by(|cur, prev| cur.key == prev.key);
    before - events.len()
}
