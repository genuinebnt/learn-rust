pub fn truncate(s: &str, max_bytes: usize) -> String {
    if s.chars().count() <= max_bytes {
        return s.to_string();
    }
    if max_bytes == 0 {
        return String::new();
    }
    let kept: String = s.chars().take(max_bytes - 1).collect();
    format!("{kept}…")
}
