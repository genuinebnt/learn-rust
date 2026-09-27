pub fn diff_ways_to_compute(expression: &str) -> Vec<i64> {
    let b = expression.as_bytes();
    if b.len() == 1 {
        return vec![i64::from(b[0] - b'0')];
    }
    let mut out = Vec::new();
    for i in 0..b.len() {
        if b[i].is_ascii_digit() {
            continue;
        }
        for a in diff_ways_to_compute(&expression[..i]) {
            for c in diff_ways_to_compute(&expression[i + 1..]) {
                out.push(match b[i] { b'+' => a + c, b'-' => a - c, _ => a * c });
            }
        }
    }
    out
}
