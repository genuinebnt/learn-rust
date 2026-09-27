pub fn word_break(s: &str, words: &[&str]) -> bool {
    let mut rest = s;
    while !rest.is_empty() {
        match words.iter().filter(|w| rest.starts_with(**w)).max_by_key(|w| w.len()) {
            Some(w) => rest = &rest[w.len()..],
            None => return false,
        }
    }
    true
}
