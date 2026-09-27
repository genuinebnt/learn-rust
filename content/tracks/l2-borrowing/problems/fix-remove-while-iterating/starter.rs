#[derive(Debug, PartialEq)]
pub struct Event {
    pub key: String,
    pub count: u32,
}

/// Merges each run of adjacent events with the same key into the run's first event, adding up the counts.
/// Returns how many events were removed.
pub fn merge_runs(events: &mut Vec<Event>) -> usize {
    let mut removed = 0;
    for (i, e) in events.iter().enumerate() {
        if i > 0 && e.key == events[i - 1].key {
            events[i - 1].count += e.count;
            events.remove(i);
            removed += 1;
        }
    }
    removed
}
