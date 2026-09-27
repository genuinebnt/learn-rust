pub fn initials(full_name: &str) -> String {
    full_name
        .split_whitespace()
        .filter_map(|w| w.chars().next())
        .map(|c| c.to_ascii_uppercase())
        .collect()
}
