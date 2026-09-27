pub fn check_valid_string(s: &str) -> bool {
    // possible[k]: some choice leaves k open after this prefix.
    let mut possible = vec![true];
    for b in s.bytes() {
        let mut next = vec![false; possible.len() + 1];
        for (k, &ok) in possible.iter().enumerate() {
            if !ok {
                continue;
            }
            if b != b')' {
                next[k + 1] = true;
            }
            if b != b'(' && k > 0 {
                next[k - 1] = true;
            }
            if b == b'*' {
                next[k] = true;
            }
        }
        possible = next;
    }
    possible[0]
}
