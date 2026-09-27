use std::collections::HashMap;

/// How many times each word appears.
pub fn word_counts(text: &str) -> HashMap<&str, usize> {
    let mut counts = HashMap::new();
    for word in text.split_whitespace() {
        if counts.contains_key(word) {
            *counts.get_mut(word).unwrap() += 1;
        } else {
            counts.insert(word, 1);
        }
    }
    counts
}
