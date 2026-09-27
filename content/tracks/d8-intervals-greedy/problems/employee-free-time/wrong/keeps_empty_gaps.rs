pub fn employee_free_time(schedule: &[Vec<(i32, i32)>]) -> Vec<(i32, i32)> {
    let mut all: Vec<(i32, i32)> = schedule.iter().flatten().copied().collect();
    all.sort_unstable();
    let mut free = Vec::new();
    let mut busy_until: Option<i32> = None;
    for (start, end) in all {
        busy_until = Some(match busy_until {
            Some(b) if start >= b => {
                free.push((b, start));
                end
            }
            Some(b) => b.max(end),
            None => end,
        });
    }
    free
}
