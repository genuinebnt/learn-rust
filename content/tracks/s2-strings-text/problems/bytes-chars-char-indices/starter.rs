/// 1-based (line, column) of byte offset `at` in `src`, with the column counted in chars.
/// `at == src.len()` is the end of the text. `None` when `at` is past the end or inside a character.
pub fn line_col(src: &str, at: usize) -> Option<(usize, usize)> {
    todo!()
}

/// The byte offset where char `n` starts, `s.len()` when `n` is the number of chars, `None` beyond that.
pub fn char_to_byte(s: &str, n: usize) -> Option<usize> {
    todo!()
}

/// Every non-overlapping occurrence of `needle` (never empty), left to right, as (byte offset, char offset).
pub fn find_all(s: &str, needle: &str) -> Vec<(usize, usize)> {
    todo!()
}
