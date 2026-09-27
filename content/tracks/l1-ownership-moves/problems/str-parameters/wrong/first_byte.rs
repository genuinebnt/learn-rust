pub fn initials(full_name: &str) -> String {
    full_name
        .split_whitespace()
        .map(|w| (w.as_bytes()[0] as char).to_ascii_uppercase())
        .collect()
}
