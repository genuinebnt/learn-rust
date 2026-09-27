/// The first `n` characters of `s`, followed by "…" if anything was cut.
pub fn preview(s: &str, n: usize) -> String {
    match s.char_indices().nth(n) {
        None => s.to_string(),
        Some((cut, _)) => format!("{}…", &s[..cut]),
    }
}

/// `s` with its first character in upper case (full Unicode rules); the rest unchanged.
pub fn capitalize(s: &str) -> String {
    let mut chars = s.chars();
    match chars.next() {
        None => String::new(),
        Some(first) => std::iter::once(first.to_ascii_uppercase()).chain(chars).collect(),
    }
}

/// All but the last 4 characters of `s` replaced by '*'.
pub fn mask(s: &str) -> String {
    let hidden = s.chars().count().saturating_sub(4);
    let keep = s.char_indices().nth(hidden).map_or(s.len(), |(i, _)| i);
    "*".repeat(hidden) + &s[keep..]
}
