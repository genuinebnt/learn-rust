use std::cmp::Reverse;
use std::collections::{BinaryHeap, HashMap};

pub fn top_k_frequent<'a>(words: &[&'a str], k: usize) -> Vec<&'a str> {
    let mut counts: HashMap<&'a str, usize> = HashMap::new();
    for &w in words {
        *counts.entry(w).or_insert(0) += 1;
    }
    // Max-heap on (Reverse(count), word): the top is the worst kept word,
    // i.e. the lowest count, and among equal counts the latest word.
    let mut heap: BinaryHeap<(Reverse<usize>, &'a str)> = BinaryHeap::with_capacity(k + 1);
    for (w, c) in counts {
        heap.push((Reverse(c), w));
        if heap.len() > k {
            heap.pop();
        }
    }
    // Ascending order of (Reverse(count), word) is the answer's order.
    heap.into_sorted_vec().into_iter().map(|(_, w)| w).collect()
}
