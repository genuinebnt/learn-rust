fn dist(a: &[u8], b: &[u8]) -> usize {
    match (a, b) {
        ([], _) => b.len(),
        (_, []) => a.len(),
        ([x, ra @ ..], [y, rb @ ..]) if x == y => dist(ra, rb),
        ([_, ra @ ..], [_, rb @ ..]) => 1 + dist(ra, b).min(dist(a, rb)),
    }
}

pub fn min_distance(a: &str, b: &str) -> usize {
    dist(a.as_bytes(), b.as_bytes())
}
