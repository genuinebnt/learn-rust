use std::cmp::Reverse;
use std::collections::BinaryHeap;

pub fn employee_free_time(schedule: &[Vec<(i32, i32)>]) -> Vec<(i32, i32)> {
    // One entry per employee: (start, employee, index) of their next interval.
    let mut heap = BinaryHeap::new();
    for (e, list) in schedule.iter().enumerate() {
        if let Some(&(start, _)) = list.first() {
            heap.push(Reverse((start, e, 0usize)));
        }
    }
    let mut free = Vec::new();
    let mut busy_until: Option<i32> = None;
    while let Some(Reverse((start, e, i))) = heap.pop() {
        let end = schedule[e][i].1;
        busy_until = Some(match busy_until {
            Some(b) if start > b => {
                free.push((b, start));
                end
            }
            Some(b) => b.max(end),
            None => end,
        });
        if let Some(&(next, _)) = schedule[e].get(i + 1) {
            heap.push(Reverse((next, e, i + 1)));
        }
    }
    free
}
