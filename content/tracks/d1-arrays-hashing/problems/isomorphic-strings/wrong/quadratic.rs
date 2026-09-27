pub fn is_isomorphic(s: &str, t: &str) -> bool {
    let (a, b) = (s.as_bytes(), t.as_bytes());
    (0..a.len()).all(|i| (i + 1..a.len()).all(|j| (a[i] == a[j]) == (b[i] == b[j])))
}
