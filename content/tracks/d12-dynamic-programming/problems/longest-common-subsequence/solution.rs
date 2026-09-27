pub fn longest_common_subsequence(a: &str, b: &str) -> usize {
    let (a, b) = (a.as_bytes(), b.as_bytes());
    // prev[j] = LCS of a[..i] and b[..j]; cur becomes row i + 1.
    let mut prev = vec![0usize; b.len() + 1];
    let mut cur = vec![0usize; b.len() + 1];
    for &x in a {
        for (j, &y) in b.iter().enumerate() {
            cur[j + 1] = if x == y { prev[j] + 1 } else { prev[j + 1].max(cur[j]) };
        }
        std::mem::swap(&mut prev, &mut cur);
    }
    prev[b.len()]
}
