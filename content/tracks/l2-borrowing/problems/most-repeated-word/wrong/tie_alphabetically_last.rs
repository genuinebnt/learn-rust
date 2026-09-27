use std::collections::HashMap;

pub fn most_repeated(text: &str) -> Option<&str> {
    let mut counts: HashMap<&str, usize> = HashMap::new();
    for w in text.split_whitespace() {
        *counts.entry(w).or_insert(0) += 1;
    }
    counts.into_iter().max_by(|a, b| a.1.cmp(&b.1).then_with(|| a.0.cmp(b.0))).map(|(w, _)| w)
}
