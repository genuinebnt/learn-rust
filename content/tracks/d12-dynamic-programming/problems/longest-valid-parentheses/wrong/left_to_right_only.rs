pub fn longest_valid_parentheses(s: &str) -> usize {
    let (mut open, mut close, mut best) = (0, 0, 0);
    for c in s.bytes() {
        if c == b'(' {
            open += 1;
        } else {
            close += 1;
        }
        if open == close {
            best = best.max(2 * close);
        } else if close > open {
            open = 0;
            close = 0;
        }
    }
    best
}
