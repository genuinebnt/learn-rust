use std::collections::BTreeMap;

pub fn index(words: &[&str]) -> BTreeMap<char, Vec<String>> {
    let mut idx: BTreeMap<char, Vec<String>> = BTreeMap::new();
    for w in words {
        if let Some(first) = w.chars().next() {
            let list = idx.entry(first.to_ascii_lowercase()).or_default();
            let at = list.binary_search(&w.to_string()).unwrap_or_else(|at| at);
            list.insert(at, w.to_string());
        }
    }
    idx
}
