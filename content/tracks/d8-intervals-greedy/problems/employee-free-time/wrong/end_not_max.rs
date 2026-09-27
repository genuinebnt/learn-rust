pub fn employee_free_time(schedule: &[Vec<(i32, i32)>]) -> Vec<(i32, i32)> {
    let mut all: Vec<(i32, i32)> = schedule.iter().flatten().copied().collect();
    all.sort_unstable();
    let mut free = Vec::new();
    for w in all.windows(2) {
        if w[1].0 > w[0].1 {
            free.push((w[0].1, w[1].0));
        }
    }
    free
}
