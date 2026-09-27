pub fn longest_common_subsequence(a: &str, b: &str) -> usize {
    let (a, b) = (a.as_bytes(), b.as_bytes());
    let mut prev = vec![0usize; b.len() + 1];
    let mut best = 0;
    for &x in a {
        let mut cur = vec![0usize; b.len() + 1];
        for (j, &y) in b.iter().enumerate() {
            if x == y {
                cur[j + 1] = prev[j] + 1;
                best = best.max(cur[j + 1]);
            }
        }
        prev = cur;
    }
    best
}
