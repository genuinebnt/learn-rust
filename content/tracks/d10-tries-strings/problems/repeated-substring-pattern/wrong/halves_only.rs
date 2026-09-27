pub fn repeated_substring_pattern(s: &str) -> bool {
    let n = s.len();
    n >= 2 && n % 2 == 0 && s[..n / 2] == s[n / 2..]
}
