pub fn truncate(s: &str, max_bytes: usize) -> String {
    if s.len() <= max_bytes {
        return s.to_string();
    }
    let Some(budget) = max_bytes.checked_sub('…'.len_utf8()) else {
        return String::new();
    };
    format!("{}…", &s[..s.floor_char_boundary(budget)])
}
