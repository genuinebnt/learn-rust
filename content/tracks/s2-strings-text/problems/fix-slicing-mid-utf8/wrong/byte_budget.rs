/// The first `n` characters of `s` (all of `s` if it's shorter).
pub fn prefix(s: &str, n: usize) -> &str {
    if s.len() <= n {
        s
    } else {
        let mut end = n;
        while !s.is_char_boundary(end) {
            end -= 1;
        }
        &s[..end]
    }
}
