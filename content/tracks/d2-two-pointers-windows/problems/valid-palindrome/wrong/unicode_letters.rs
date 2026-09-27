pub fn is_palindrome(s: &str) -> bool {
    let kept: Vec<char> = s.chars().filter(|c| c.is_alphanumeric()).flat_map(|c| c.to_lowercase()).collect();
    kept.iter().eq(kept.iter().rev())
}
