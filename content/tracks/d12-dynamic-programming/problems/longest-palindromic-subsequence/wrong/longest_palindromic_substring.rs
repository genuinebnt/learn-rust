pub fn longest_palindrome_subseq(s: &str) -> usize {
    let s = s.as_bytes();
    let n = s.len();
    let mut best = n.min(1);
    for center in 0..2 * n {
        let (mut lo, mut hi) = (center / 2, center / 2 + center % 2);
        while hi < n && s[lo] == s[hi] {
            best = best.max(hi - lo + 1);
            if lo == 0 {
                break;
            }
            lo -= 1;
            hi += 1;
        }
    }
    best
}
