pub fn schedule_course(courses: &[(u32, u32)]) -> usize {
    let mut by_deadline = courses.to_vec();
    by_deadline.sort_unstable_by_key(|&(_, last_day)| last_day);
    let mut taken: Vec<u32> = Vec::new();
    let mut time = 0u64;
    for (duration, last_day) in by_deadline {
        taken.push(duration);
        time += duration as u64;
        if time > last_day as u64 {
            let longest = (0..taken.len()).max_by_key(|&i| taken[i]).unwrap();
            time -= taken.swap_remove(longest) as u64;
        }
    }
    taken.len()
}
