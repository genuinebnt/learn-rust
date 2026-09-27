use std::collections::BinaryHeap;

pub fn schedule_course(courses: &[(u32, u32)]) -> usize {
    let mut by_deadline = courses.to_vec();
    by_deadline.sort_unstable_by_key(|&(_, last_day)| last_day);
    let mut taken = BinaryHeap::new();
    let mut time = 0u32;
    for (duration, last_day) in by_deadline {
        taken.push(duration);
        time += duration;
        if time > last_day {
            if let Some(longest) = taken.pop() {
                time -= longest;
            }
        }
    }
    taken.len()
}
