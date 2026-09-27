pub fn by_len_then_alpha(words: &mut [String]) {
    words.sort_by_key(|w| w.len());
}
