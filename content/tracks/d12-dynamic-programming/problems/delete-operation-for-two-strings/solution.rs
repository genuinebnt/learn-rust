pub fn min_distance(a: &str, b: &str) -> usize {
    let (x, y) = (a.as_bytes(), b.as_bytes());
    let mut prev = vec![0usize; y.len() + 1];
    let mut cur = vec![0usize; y.len() + 1];
    for &p in x {
        for (j, &q) in y.iter().enumerate() {
            cur[j + 1] = if p == q { prev[j] + 1 } else { prev[j + 1].max(cur[j]) };
        }
        std::mem::swap(&mut prev, &mut cur);
    }
    // Keep the longest common subsequence; delete everything else.
    let lcs = prev[y.len()];
    x.len() + y.len() - 2 * lcs
}
