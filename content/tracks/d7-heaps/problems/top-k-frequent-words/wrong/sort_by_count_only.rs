use std::collections::HashMap;

pub fn top_k_frequent<'a>(words: &[&'a str], k: usize) -> Vec<&'a str> {
    let mut counts: HashMap<&'a str, usize> = HashMap::new();
    for &w in words {
        *counts.entry(w).or_insert(0) += 1;
    }
    let mut all: Vec<(&'a str, usize)> = counts.into_iter().collect();
    all.sort_by(|a, b| b.1.cmp(&a.1));
    all.into_iter().take(k).map(|(w, _)| w).collect()
}
