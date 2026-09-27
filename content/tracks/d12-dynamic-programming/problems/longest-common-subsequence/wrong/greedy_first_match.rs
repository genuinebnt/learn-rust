pub fn longest_common_subsequence(a: &str, b: &str) -> usize {
    let b = b.as_bytes();
    let (mut j, mut count) = (0, 0);
    for &x in a.as_bytes() {
        if let Some(k) = b[j..].iter().position(|&y| y == x) {
            j += k + 1;
            count += 1;
        }
    }
    count
}
