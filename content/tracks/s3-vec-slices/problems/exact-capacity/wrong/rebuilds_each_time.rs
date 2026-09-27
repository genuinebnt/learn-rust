pub fn join_with(parts: &[&str], sep: &str) -> String {
    let mut out = String::new();
    for (i, p) in parts.iter().enumerate() {
        out = if i == 0 { p.to_string() } else { format!("{out}{sep}{p}") };
    }
    out.shrink_to_fit();
    out
}
