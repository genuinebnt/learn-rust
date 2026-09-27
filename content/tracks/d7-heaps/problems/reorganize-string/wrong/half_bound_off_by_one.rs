use std::collections::{BinaryHeap, HashMap};

pub fn reorganize(s: &str) -> Option<String> {
    let mut counts: HashMap<char, usize> = HashMap::new();
    for c in s.chars() {
        *counts.entry(c).or_insert(0) += 1;
    }
    let len = s.chars().count();
    if counts.values().any(|&k| k > len / 2) && len > 1 {
        return None;
    }
    let mut heap: BinaryHeap<(usize, char)> = counts.into_iter().map(|(c, k)| (k, c)).collect();
    let mut out = String::new();
    let mut held: Option<(usize, char)> = None;
    while let Some((k, c)) = heap.pop() {
        out.push(c);
        if let Some(h) = held.take() {
            heap.push(h);
        }
        if k > 1 {
            held = Some((k - 1, c));
        }
    }
    Some(out)
}
