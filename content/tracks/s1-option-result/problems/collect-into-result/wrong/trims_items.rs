pub fn parse_all(items: &[&str]) -> Result<Vec<i32>, String> {
    items
        .iter()
        .map(|s| s.trim().parse().map_err(|_| format!("bad number: {s}")))
        .collect()
}
