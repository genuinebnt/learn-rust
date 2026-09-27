pub fn longest_palindrome(s: &str) -> &str {
    let b = s.as_bytes();
    let (mut lo, mut hi) = (0, 0);
    for i in 0..b.len() {
        for (mut l, mut r) in [(i, i + 1), (i, i)] {
            while l > 0 && r < b.len() && b[l - 1] == b[r] {
                l -= 1;
                r += 1;
            }
            if r - l > hi - lo {
                (lo, hi) = (l, r);
            }
        }
    }
    &s[lo..hi]
}
