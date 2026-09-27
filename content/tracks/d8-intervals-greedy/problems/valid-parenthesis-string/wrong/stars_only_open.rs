pub fn check_valid_string(s: &str) -> bool {
    let mut open = 0i64;
    for b in s.bytes() {
        if b == b')' {
            open -= 1;
        } else {
            open += 1;
        }
        if open < 0 {
            return false;
        }
    }
    true
}
