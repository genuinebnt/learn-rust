pub fn check_valid_string(s: &str) -> bool {
    let (mut lo, mut hi) = (0i64, 0i64);
    for b in s.bytes() {
        match b {
            b'(' => {
                lo += 1;
                hi += 1;
            }
            b')' => {
                lo -= 1;
                hi -= 1;
            }
            _ => {
                lo -= 1;
                hi += 1;
            }
        }
        if hi < 0 {
            return false;
        }
    }
    lo <= 0
}
