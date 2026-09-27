#[derive(Debug, Clone, PartialEq)]
pub struct Job {
    pub id: u32,
    pub retries_left: u32,
}

/// One scheduler tick: every job uses up one retry, and jobs left with none are removed. One pass.
pub fn tick(jobs: &mut Vec<Job>) {
    jobs.retain_mut(|job| {
        job.retries_left = job.retries_left.saturating_sub(1);
        job.retries_left > 0
    });
}

#[derive(Debug, Clone, PartialEq)]
pub struct Run {
    pub key: char,
    pub count: u32,
}

/// Merges each stretch of neighbouring runs with the same key into its first run, adding up the counts.
pub fn merge_runs(runs: &mut Vec<Run>) {
    runs.dedup_by(|next, kept| {
        if next.key == kept.key {
            kept.count += next.count;
            true
        } else {
            false
        }
    });
}

/// Keeps only the first event of each stretch of consecutive events in the same minute (seconds / 60).
pub fn first_per_minute(events: &mut Vec<(u64, String)>) {
    let mut seen = std::collections::HashSet::new();
    events.retain(|e| seen.insert(e.0 / 60));
}
