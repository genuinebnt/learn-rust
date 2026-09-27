use std::collections::HashSet;

pub fn is_anagram(s: &str, t: &str) -> bool {
    s.len() == t.len() && s.bytes().collect::<HashSet<_>>() == t.bytes().collect::<HashSet<_>>()
}
