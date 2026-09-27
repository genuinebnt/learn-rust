use std::collections::HashSet;

pub fn word_break(s: &str, words: &[&str]) -> bool {
    let dict: HashSet<&str> = words.iter().copied().collect();
    let mut ok = vec![false; s.len() + 1];
    ok[0] = true;
    for end in 1..=s.len() {
        ok[end] = (end.saturating_sub(20)..end).any(|start| ok[start] && dict.contains(&s[start..end]));
    }
    ok[s.len()]
}
