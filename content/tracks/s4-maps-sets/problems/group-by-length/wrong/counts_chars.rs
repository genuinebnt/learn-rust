use std::collections::HashMap;

pub fn group_by_len<'a>(words: &[&'a str]) -> HashMap<usize, Vec<&'a str>> {
    let mut groups: HashMap<usize, Vec<&'a str>> = HashMap::new();
    for &w in words {
        groups.entry(w.chars().count()).or_default().push(w);
    }
    groups
}
