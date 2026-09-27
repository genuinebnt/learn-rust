use std::collections::HashMap;

/// How many times each word appears.
pub fn word_counts(text: &str) -> HashMap<&str, usize> {
    let mut counts = HashMap::new();
    for word in text.split(' ') {
        *counts.entry(word).or_insert(0) += 1;
    }
    counts
}
