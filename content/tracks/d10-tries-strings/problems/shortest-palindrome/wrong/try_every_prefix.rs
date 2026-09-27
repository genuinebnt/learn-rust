pub fn shortest_palindrome(s: &str) -> String {
    let chars: Vec<char> = s.chars().collect();
    let keep = (0..=chars.len()).rev().find(|&k| chars[..k].iter().eq(chars[..k].iter().rev())).unwrap_or(0);
    chars[keep..].iter().rev().chain(&chars).collect()
}
