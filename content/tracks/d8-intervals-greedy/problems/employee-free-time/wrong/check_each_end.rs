pub fn employee_free_time(schedule: &[Vec<(i32, i32)>]) -> Vec<(i32, i32)> {
    let all: Vec<(i32, i32)> = schedule.iter().flatten().copied().collect();
    let mut free = Vec::new();
    for &(_, end) in &all {
        // Free from `end` if nobody works at `end` and somebody starts later.
        if all.iter().any(|&(s, e)| s <= end && end < e) {
            continue;
        }
        if let Some(next) = all.iter().map(|&(s, _)| s).filter(|&s| s > end).min() {
            free.push((end, next));
        }
    }
    free.sort_unstable();
    free.dedup();
    free
}
