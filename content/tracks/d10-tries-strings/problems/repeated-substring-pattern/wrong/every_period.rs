pub fn repeated_substring_pattern(s: &str) -> bool {
    let b = s.as_bytes();
    let n = b.len();
    (1..=n / 2).any(|p| (p..n).all(|i| b[i] == b[i - p]) && n % p == 0)
}
