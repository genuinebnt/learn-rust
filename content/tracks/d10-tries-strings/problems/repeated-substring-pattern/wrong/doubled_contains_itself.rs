pub fn repeated_substring_pattern(s: &str) -> bool {
    s.len() >= 2 && format!("{s}{s}").contains(s)
}
