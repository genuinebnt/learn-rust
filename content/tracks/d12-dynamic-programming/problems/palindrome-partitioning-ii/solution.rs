pub fn min_cut(s: &str) -> usize {
    let s = s.as_bytes();
    let n = s.len();
    // pieces[k] = the fewest palindromes that s[..k] splits into.
    let mut pieces: Vec<usize> = (0..=n).collect();
    for center in 0..n {
        // Odd palindromes around s[center], then even ones around s[center], s[center + 1].
        for (mut lo, mut hi) in [(center, center), (center, center + 1)] {
            while hi < n && s[lo] == s[hi] {
                // s[lo..=hi] is a palindrome: s[..lo] then this piece.
                pieces[hi + 1] = pieces[hi + 1].min(pieces[lo] + 1);
                if lo == 0 {
                    break;
                }
                lo -= 1;
                hi += 1;
            }
        }
    }
    pieces[n].saturating_sub(1)
}
