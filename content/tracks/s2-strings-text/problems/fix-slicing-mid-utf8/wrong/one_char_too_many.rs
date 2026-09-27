/// The first `n` characters of `s` (all of `s` if it's shorter).
pub fn prefix(s: &str, n: usize) -> &str {
    match s.char_indices().nth(n) {
        Some((i, c)) => &s[..i + c.len_utf8()],
        None => s,
    }
}
