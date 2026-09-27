fn lcs(a: &[u8], b: &[u8]) -> usize {
    match (a, b) {
        ([], _) | (_, []) => 0,
        ([x, ra @ ..], [y, rb @ ..]) if x == y => 1 + lcs(ra, rb),
        ([_, ra @ ..], [_, rb @ ..]) => lcs(ra, b).max(lcs(a, rb)),
    }
}

pub fn longest_common_subsequence(a: &str, b: &str) -> usize {
    lcs(a.as_bytes(), b.as_bytes())
}
