/// `border[i]`: length of the longest proper prefix of `needle[..=i]` that is also a suffix of it.
fn borders<T: PartialEq>(needle: &[T]) -> Vec<usize> {
    let mut border = vec![0; needle.len()];
    let mut k = 0;
    for i in 1..needle.len() {
        while k > 0 && needle[i] != needle[k] {
            k = border[k - 1];
        }
        if needle[i] == needle[k] {
            k += 1;
        }
        border[i] = k;
    }
    border
}

pub fn find_first<T: PartialEq>(haystack: &[T], needle: &[T]) -> Option<usize> {
    if needle.is_empty() {
        return Some(0);
    }
    let border = borders(needle);
    // `k` items of the needle are matched so far; a mismatch falls back to a shorter border, never re-reads the haystack.
    let mut k = 0;
    for (i, x) in haystack.iter().enumerate() {
        while k > 0 && *x != needle[k] {
            k = border[k - 1];
        }
        if *x == needle[k] {
            k += 1;
            if k == needle.len() {
                return Some(i + 1 - k);
            }
        }
    }
    None
}
