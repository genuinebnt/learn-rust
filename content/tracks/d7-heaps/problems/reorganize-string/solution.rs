use std::collections::{BinaryHeap, HashMap};

pub fn reorganize(s: &str) -> Option<String> {
    let mut counts: HashMap<char, usize> = HashMap::new();
    for c in s.chars() {
        *counts.entry(c).or_insert(0) += 1;
    }
    let mut heap: BinaryHeap<(usize, char)> = counts.into_iter().map(|(c, k)| (k, c)).collect();
    let mut out = String::with_capacity(s.len());
    // The character just placed sits out one step so it can't come next.
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
    // Copies still held at the end had nothing to separate them.
    held.is_none().then_some(out)
}
