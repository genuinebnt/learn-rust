pub fn by_len_then_alpha(words: &mut [String]) {
    words.sort_by(|a, b| a.len().cmp(&b.len()).then_with(|| a.cmp(b)));
}
