pub fn check_valid_string(s: &str) -> bool {
    // lo..=hi: the open counts some choice of stars can reach.
    let (mut lo, mut hi) = (0usize, 0usize);
    for b in s.bytes() {
        match b {
            b'(' => {
                lo += 1;
                hi += 1;
            }
            b')' => {
                if hi == 0 {
                    return false;
                }
                lo = lo.saturating_sub(1);
                hi -= 1;
            }
            _ => {
                lo = lo.saturating_sub(1);
                hi += 1;
            }
        }
    }
    lo == 0
}
