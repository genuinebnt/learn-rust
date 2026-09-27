pub fn longest_valid_parentheses(s: &str) -> usize {
    let b = s.as_bytes();
    let mut best = 0;
    for i in 0..b.len() {
        let mut depth = 0i32;
        for j in i..b.len() {
            depth += if b[j] == b'(' { 1 } else { -1 };
            if depth < 0 {
                break;
            }
            if depth == 0 {
                best = best.max(j + 1 - i);
            }
        }
    }
    best
}
