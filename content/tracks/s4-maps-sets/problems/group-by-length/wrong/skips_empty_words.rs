use std::collections::HashMap;

pub fn group_by_len<'a>(words: &[&'a str]) -> HashMap<usize, Vec<&'a str>> {
    let mut groups: HashMap<usize, Vec<&'a str>> = HashMap::new();
    for &w in words.iter().filter(|w| !w.is_empty()) {
        groups.entry(w.len()).or_default().push(w);
    }
    groups
}
