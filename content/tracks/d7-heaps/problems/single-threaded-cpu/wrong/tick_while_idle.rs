use std::cmp::Reverse;
use std::collections::BinaryHeap;

pub fn get_order(tasks: &[(u32, u32)]) -> Vec<usize> {
    let mut arrivals: Vec<usize> = (0..tasks.len()).collect();
    arrivals.sort_unstable_by_key(|&i| (tasks[i].0, i));
    let mut waiting: BinaryHeap<Reverse<(u32, usize)>> = BinaryHeap::new();
    let mut out = Vec::new();
    let mut clock: u64 = 0;
    let mut next = 0;
    while out.len() < tasks.len() {
        while next < arrivals.len() && tasks[arrivals[next]].0 as u64 <= clock {
            let i = arrivals[next];
            waiting.push(Reverse((tasks[i].1, i)));
            next += 1;
        }
        match waiting.pop() {
            Some(Reverse((time, i))) => {
                clock += time as u64;
                out.push(i);
            }
            // Nothing waiting: let one unit of time pass.
            None => clock += 1,
        }
    }
    out
}
