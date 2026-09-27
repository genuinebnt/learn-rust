fn dist(a: &[char], b: &[char]) -> usize {
    match (a, b) {
        ([], _) => b.len(),
        (_, []) => a.len(),
        ([x, ra @ ..], [y, rb @ ..]) if x == y => dist(ra, rb),
        ([_, ra @ ..], [_, rb @ ..]) => 1 + dist(ra, rb).min(dist(ra, b)).min(dist(a, rb)),
    }
}

pub fn edit_distance(a: &str, b: &str) -> usize {
    let a: Vec<char> = a.chars().collect();
    let b: Vec<char> = b.chars().collect();
    dist(&a, &b)
}
