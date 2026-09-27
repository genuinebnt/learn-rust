pub fn is_palindrome(s: &str) -> bool {
    let b = s.as_bytes();
    let (mut l, mut r) = (0, b.len());
    while l < r {
        if !b[l].is_ascii_alphabetic() {
            l += 1;
        } else if !b[r - 1].is_ascii_alphabetic() {
            r -= 1;
        } else if !b[l].eq_ignore_ascii_case(&b[r - 1]) {
            return false;
        } else {
            l += 1;
            r -= 1;
        }
    }
    true
}
