#[derive(Debug, Clone, PartialEq)]
pub struct Job {
    pub id: u32,
    pub retries_left: u32,
}

/// One scheduler tick: every job uses up one retry, and jobs left with none are removed. One pass.
pub fn tick(jobs: &mut Vec<Job>) {
    todo!()
}

#[derive(Debug, Clone, PartialEq)]
pub struct Run {
    pub key: char,
    pub count: u32,
}

/// Merges each stretch of neighbouring runs with the same key into its first run, adding up the counts.
pub fn merge_runs(runs: &mut Vec<Run>) {
    todo!()
}

/// Keeps only the first event of each stretch of consecutive events in the same minute (seconds / 60).
pub fn first_per_minute(events: &mut Vec<(u64, String)>) {
    todo!()
}
