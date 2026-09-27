use std::collections::HashSet;

pub fn longest_word<'a>(words: &[&'a str]) -> &'a str {
    let set: HashSet<&str> = words.iter().copied().collect();
    let mut best = "";
    for &w in words {
        if (1..=w.len()).all(|k| set.contains(&w[..k])) && w.len() >= best.len() {
            best = w;
        }
    }
    best
}
