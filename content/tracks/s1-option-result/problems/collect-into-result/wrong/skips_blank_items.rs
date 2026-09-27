pub fn parse_all(items: &[&str]) -> Result<Vec<i32>, String> {
    items
        .iter()
        .filter(|s| !s.is_empty())
        .map(|s| s.parse().map_err(|_| format!("bad number: {s}")))
        .collect()
}
