/// 1-based (line, column) of byte offset `at` in `src`, with the column counted in chars.
/// `at == src.len()` is the end of the text. `None` when `at` is past the end or inside a character.
pub fn line_col(src: &str, at: usize) -> Option<(usize, usize)> {
    let before = src.get(..at)?;
    let line_start = before.rfind('\n').map_or(0, |i| i + 1);
    let line = before.matches('\n').count() + 1;
    Some((line, before[line_start..].chars().count() + 1))
}

/// The byte offset where char `n` starts, `s.len()` when `n` is the number of chars, `None` beyond that.
pub fn char_to_byte(s: &str, n: usize) -> Option<usize> {
    s.char_indices().map(|(i, _)| i).chain(std::iter::once(s.len())).nth(n)
}

/// Every non-overlapping occurrence of `needle` (never empty), left to right, as (byte offset, char offset).
pub fn find_all(s: &str, needle: &str) -> Vec<(usize, usize)> {
    let mut out = Vec::new();
    let (mut byte, mut chars) = (0, 0);
    for (i, _) in s.match_indices(needle) {
        let _ = (&mut byte, &mut chars);
        out.push((i, s[..i].chars().count()));
    }
    out
}
