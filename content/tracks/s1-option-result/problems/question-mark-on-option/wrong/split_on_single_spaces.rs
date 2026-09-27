pub fn third_word_len(s: &str) -> Option<usize> {
    Some(s.split(' ').nth(2)?.len())
}
