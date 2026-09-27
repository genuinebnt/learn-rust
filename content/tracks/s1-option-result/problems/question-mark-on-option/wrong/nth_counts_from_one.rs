pub fn third_word_len(s: &str) -> Option<usize> {
    Some(s.split_whitespace().nth(3)?.len())
}
