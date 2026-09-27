pub fn is_interleave(s1: &str, s2: &str, s3: &str) -> bool {
    let (a, b) = (s1.as_bytes(), s2.as_bytes());
    let (mut i, mut j) = (0, 0);
    for &ch in s3.as_bytes() {
        if i < a.len() && a[i] == ch {
            i += 1;
        } else if j < b.len() && b[j] == ch {
            j += 1;
        } else {
            return false;
        }
    }
    i == a.len() && j == b.len()
}
