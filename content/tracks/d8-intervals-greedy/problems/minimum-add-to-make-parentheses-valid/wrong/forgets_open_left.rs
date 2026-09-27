pub fn min_add_to_make_valid(s: &str) -> usize {
    let (mut open, mut added) = (0usize, 0usize);
    for b in s.bytes() {
        if b == b'(' {
            open += 1;
        } else if open > 0 {
            open -= 1;
        } else {
            added += 1;
        }
    }
    added
}
