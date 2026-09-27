use std::cmp::Reverse;
use std::collections::BinaryHeap;

pub fn get_order(tasks: &[(u32, u32)]) -> Vec<usize> {
    let mut arrivals: Vec<usize> = (0..tasks.len()).collect();
    arrivals.sort_unstable_by_key(|&i| (tasks[i].0, i));
    let mut waiting: BinaryHeap<Reverse<(u32, usize)>> = BinaryHeap::new();
    let mut out = Vec::new();
    let mut clock: u32 = 0;
    let mut next = 0;
    while out.len() < tasks.len() {
        if waiting.is_empty() {
            clock = clock.max(tasks[arrivals[next]].0);
        }
        while next < arrivals.len() && tasks[arrivals[next]].0 <= clock {
            let i = arrivals[next];
            waiting.push(Reverse((tasks[i].1, i)));
            next += 1;
        }
        if let Some(Reverse((time, i))) = waiting.pop() {
            clock += time;
            out.push(i);
        }
    }
    out
}
