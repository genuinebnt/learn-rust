fn lps(s: &[u8]) -> usize {
    match s {
        [] => 0,
        [_] => 1,
        [a, mid @ .., b] if a == b => 2 + lps(mid),
        [_, rest @ ..] => lps(rest).max(lps(&s[..s.len() - 1])),
    }
}

pub fn longest_palindrome_subseq(s: &str) -> usize {
    lps(s.as_bytes())
}
