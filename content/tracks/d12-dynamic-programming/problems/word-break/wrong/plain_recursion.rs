pub fn word_break(s: &str, words: &[&str]) -> bool {
    s.is_empty() || words.iter().any(|w| s.starts_with(w) && word_break(&s[w.len()..], words))
}
