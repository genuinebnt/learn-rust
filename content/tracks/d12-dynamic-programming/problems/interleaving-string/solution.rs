pub fn is_interleave(s1: &str, s2: &str, s3: &str) -> bool {
    let (a, b, c) = (s1.as_bytes(), s2.as_bytes(), s3.as_bytes());
    if a.len() + b.len() != c.len() {
        return false;
    }
    // ok[j] for the current i: a[..i] and b[..j] interleave into c[..i + j].
    let mut ok = vec![false; b.len() + 1];
    for i in 0..=a.len() {
        for j in 0..=b.len() {
            ok[j] = if i == 0 && j == 0 {
                true
            } else {
                (i > 0 && ok[j] && a[i - 1] == c[i + j - 1]) || (j > 0 && ok[j - 1] && b[j - 1] == c[i + j - 1])
            };
        }
    }
    ok[b.len()]
}
