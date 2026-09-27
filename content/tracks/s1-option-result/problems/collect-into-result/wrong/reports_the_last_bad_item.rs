pub fn parse_all(items: &[&str]) -> Result<Vec<i32>, String> {
    let mut out = Vec::new();
    let mut err = None;
    for s in items {
        match s.parse() {
            Ok(n) => out.push(n),
            Err(_) => err = Some(format!("bad number: {s}")),
        }
    }
    match err {
        Some(e) => Err(e),
        None => Ok(out),
    }
}
