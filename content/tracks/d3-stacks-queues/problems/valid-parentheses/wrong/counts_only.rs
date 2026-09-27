pub fn is_valid(s: &str) -> bool {
    let mut open = [0i64; 3];
    for b in s.bytes() {
        let (i, d) = match b {
            b'(' => (0, 1),
            b')' => (0, -1),
            b'[' => (1, 1),
            b']' => (1, -1),
            b'{' => (2, 1),
            _ => (2, -1),
        };
        open[i] += d;
        if open[i] < 0 {
            return false;
        }
    }
    open == [0, 0, 0]
}
