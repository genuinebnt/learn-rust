use std::collections::HashMap;

pub fn group_anagrams(words: &[&str]) -> Vec<Vec<String>> {
    let mut groups: HashMap<Vec<u8>, Vec<String>> = HashMap::new();
    for &w in words {
        let mut key = w.as_bytes().to_vec();
        key.sort_unstable();
        groups.entry(key).or_default().push(w.to_string());
    }
    let mut out: Vec<Vec<String>> = groups.into_values().collect();
    for g in &mut out {
        g.sort();
    }
    out.sort();
    out
}
