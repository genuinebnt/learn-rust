pub fn longest_palindrome_subseq(s: &str) -> usize {
    let s = s.as_bytes();
    let n = s.len();
    // For the current i, best[j] = LPS of s[i..=j]. Before updating it holds s[i + 1..=j].
    let mut best = vec![0usize; n];
    for i in (0..n).rev() {
        best[i] = 1;
        let mut inner = 0; // LPS of s[i + 1..=j - 1]
        for j in i + 1..n {
            let without_i = best[j];
            best[j] = if s[i] == s[j] { inner + 2 } else { without_i.max(best[j - 1]) };
            inner = without_i;
        }
    }
    best.last().copied().unwrap_or(0)
}
