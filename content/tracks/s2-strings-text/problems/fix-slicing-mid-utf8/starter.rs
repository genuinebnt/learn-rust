/// The first `n` characters of `s`, followed by "…" if anything was cut.
pub fn preview(s: &str, n: usize) -> String {
    if s.len() <= n {
        s.to_string()
    } else {
        format!("{}…", &s[..n])
    }
}

/// `s` with its first character in upper case (full Unicode rules); the rest unchanged.
pub fn capitalize(s: &str) -> String {
    s[..1].to_uppercase() + &s[1..]
}

/// All but the last 4 characters of `s` replaced by '*'.
pub fn mask(s: &str) -> String {
    let keep = s.len().saturating_sub(4);
    "*".repeat(keep) + &s[keep..]
}
