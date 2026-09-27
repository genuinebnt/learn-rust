pub fn find_first<T: PartialEq>(haystack: &[T], needle: &[T]) -> Option<usize> {
    if needle.is_empty() {
        return Some(0);
    }
    let mut k = 0;
    for (i, x) in haystack.iter().enumerate() {
        if *x == needle[k] {
            k += 1;
            if k == needle.len() {
                return Some(i + 1 - k);
            }
        } else {
            k = 0;
        }
    }
    None
}
