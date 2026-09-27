pub fn repeated_substring_pattern(s: &str) -> bool {
    let b = s.as_bytes();
    let n = b.len();
    if n < 2 {
        return false;
    }
    // KMP border table: border[i] is the longest proper prefix of b[..=i] that is also its suffix.
    let mut border = vec![0; n];
    let mut k = 0;
    for i in 1..n {
        while k > 0 && b[i] != b[k] {
            k = border[k - 1];
        }
        if b[i] == b[k] {
            k += 1;
        }
        border[i] = k;
    }
    // The smallest period of s; s is a repetition exactly when that period divides n (and isn't n itself).
    let period = n - border[n - 1];
    period < n && n % period == 0
}
