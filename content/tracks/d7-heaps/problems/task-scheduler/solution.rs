use std::collections::{BinaryHeap, HashMap, VecDeque};

fn counts(tasks: &[char]) -> HashMap<char, usize> {
    let mut counts = HashMap::new();
    for &c in tasks {
        *counts.entry(c).or_insert(0) += 1;
    }
    counts
}

pub fn least_interval(tasks: &[char], n: usize) -> usize {
    let counts = counts(tasks);
    let Some(&most) = counts.values().max() else {
        return 0;
    };
    let tied = counts.values().filter(|&&c| c == most).count();
    // `most - 1` full frames of n + 1 slots, then one slot per task tied for most.
    tasks.len().max((most - 1) * (n + 1) + tied)
}

pub fn schedule(tasks: &[char], n: usize) -> Vec<Option<char>> {
    // Ready tasks, most runs left first.
    let mut ready: BinaryHeap<(usize, char)> = counts(tasks).into_iter().map(|(c, left)| (left, c)).collect();
    // Tasks cooling down: (first slot they may run in, runs left, id). One task starts per slot,
    // so the queue is already in time order.
    let mut cooling: VecDeque<(usize, usize, char)> = VecDeque::new();
    let mut out = Vec::with_capacity(tasks.len());
    while !ready.is_empty() || !cooling.is_empty() {
        let t = out.len();
        while let Some(&(at, left, c)) = cooling.front() {
            if at > t {
                break;
            }
            cooling.pop_front();
            ready.push((left, c));
        }
        match ready.pop() {
            Some((left, c)) => {
                out.push(Some(c));
                if left > 1 {
                    cooling.push_back((t + n + 1, left - 1, c));
                }
            }
            None => out.push(None),
        }
    }
    out
}
