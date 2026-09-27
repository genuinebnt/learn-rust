pub fn longest_valid_parentheses(s: &str) -> usize {
    // Counts every matched pair, even when they aren't next to each other.
    let mut open = 0;
    let mut pairs = 0;
    for c in s.bytes() {
        if c == b'(' {
            open += 1;
        } else if open > 0 {
            open -= 1;
            pairs += 1;
        }
    }
    2 * pairs
}
