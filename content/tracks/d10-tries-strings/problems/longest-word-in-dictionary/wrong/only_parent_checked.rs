use std::collections::HashSet;

pub fn longest_word<'a>(words: &[&'a str]) -> &'a str {
    let set: HashSet<&str> = words.iter().copied().collect();
    let mut best = "";
    for &w in words {
        let ok = w.len() == 1 || set.contains(&w[..w.len() - 1]);
        if ok && (w.len() > best.len() || (w.len() == best.len() && w < best)) {
            best = w;
        }
    }
    best
}
