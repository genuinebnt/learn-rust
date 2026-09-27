pub fn longest_valid_parentheses(s: &str) -> usize {
    let b = s.as_bytes();
    // run[i] = the length of the longest valid substring ending exactly at i.
    let mut run = vec![0usize; b.len()];
    for i in 1..b.len() {
        if b[i] != b')' {
            continue;
        }
        // Jump back over the valid run ending at i - 1 (empty if b[i - 1] is '(').
        // The byte before it must be the '(' that this ')' closes.
        if let Some(open) = i.checked_sub(run[i - 1] + 1) {
            if b[open] == b'(' {
                // The run ending just before that '(' joins on too: "()" + "(())".
                let before = if open > 0 { run[open - 1] } else { 0 };
                run[i] = run[i - 1] + 2 + before;
            }
        }
    }
    run.into_iter().max().unwrap_or(0)
}
