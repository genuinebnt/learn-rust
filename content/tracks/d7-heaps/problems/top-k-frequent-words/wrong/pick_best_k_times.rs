use std::collections::HashMap;

pub fn top_k_frequent<'a>(words: &[&'a str], k: usize) -> Vec<&'a str> {
    let mut counts: HashMap<&'a str, usize> = HashMap::new();
    for &w in words {
        *counts.entry(w).or_insert(0) += 1;
    }
    let mut left: Vec<(&'a str, usize)> = counts.into_iter().collect();
    let mut out = Vec::new();
    while out.len() < k && !left.is_empty() {
        let mut best = 0;
        for i in 1..left.len() {
            if left[i].1 > left[best].1 || (left[i].1 == left[best].1 && left[i].0 < left[best].0) {
                best = i;
            }
        }
        out.push(left.swap_remove(best).0);
    }
    out
}
