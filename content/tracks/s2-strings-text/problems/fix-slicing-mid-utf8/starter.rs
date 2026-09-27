/// The first `n` characters of `s` (all of `s` if it's shorter).
pub fn prefix(s: &str, n: usize) -> &str {
    if s.len() <= n {
        s
    } else {
        &s[..n]
    }
}
