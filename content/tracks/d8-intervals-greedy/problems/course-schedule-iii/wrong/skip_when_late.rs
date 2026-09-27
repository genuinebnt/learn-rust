pub fn schedule_course(courses: &[(u32, u32)]) -> usize {
    let mut by_deadline = courses.to_vec();
    by_deadline.sort_unstable_by_key(|&(_, last_day)| last_day);
    let (mut time, mut count) = (0u64, 0);
    for (duration, last_day) in by_deadline {
        if time + duration as u64 <= last_day as u64 {
            time += duration as u64;
            count += 1;
        }
    }
    count
}
