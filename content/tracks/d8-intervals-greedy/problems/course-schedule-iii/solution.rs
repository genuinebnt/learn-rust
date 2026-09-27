use std::collections::BinaryHeap;

pub fn schedule_course(courses: &[(u32, u32)]) -> usize {
    let mut by_deadline = courses.to_vec();
    by_deadline.sort_unstable_by_key(|&(_, last_day)| last_day);
    // Durations of the courses taken so far; a max-heap.
    let mut taken = BinaryHeap::new();
    let mut time = 0u64;
    for (duration, last_day) in by_deadline {
        taken.push(duration);
        time += duration as u64;
        if time > last_day as u64 {
            // Too late: drop the longest course (maybe this one).
            if let Some(longest) = taken.pop() {
                time -= longest as u64;
            }
        }
    }
    taken.len()
}
