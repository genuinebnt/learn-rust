use std::collections::HashSet;

pub fn word_break(s: &str, words: &[&str]) -> bool {
    let dict: HashSet<&[u8]> = words.iter().map(|w| w.as_bytes()).collect();
    let longest = words.iter().map(|w| w.len()).max().unwrap_or(0);
    let s = s.as_bytes();
    // ok[end]: the first `end` bytes split into words.
    let mut ok = vec![false; s.len() + 1];
    ok[0] = true;
    for end in 1..=s.len() {
        let first = end.saturating_sub(longest);
        ok[end] = (first..end).any(|start| ok[start] && dict.contains(&s[start..end]));
    }
    ok[s.len()]
}
