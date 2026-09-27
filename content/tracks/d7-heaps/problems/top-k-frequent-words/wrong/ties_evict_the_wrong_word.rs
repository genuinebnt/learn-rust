use std::cmp::Reverse;
use std::collections::{BinaryHeap, HashMap};

pub fn top_k_frequent<'a>(words: &[&'a str], k: usize) -> Vec<&'a str> {
    let mut counts: HashMap<&'a str, usize> = HashMap::new();
    for &w in words {
        *counts.entry(w).or_insert(0) += 1;
    }
    // Min-heap on (count, word): pops the lowest count, but on ties the *earliest* word.
    let mut heap: BinaryHeap<Reverse<(usize, &'a str)>> = BinaryHeap::new();
    for (w, c) in counts {
        heap.push(Reverse((c, w)));
        if heap.len() > k {
            heap.pop();
        }
    }
    let mut out: Vec<(usize, &str)> = heap.into_iter().map(|Reverse(x)| x).collect();
    out.sort_by(|a, b| b.0.cmp(&a.0).then(a.1.cmp(b.1)));
    out.into_iter().map(|(_, w)| w).collect()
}
