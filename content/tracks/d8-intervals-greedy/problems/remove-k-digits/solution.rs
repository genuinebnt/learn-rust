pub fn remove_kdigits(num: &str, k: usize) -> String {
    let mut k = k;
    let mut stack: Vec<u8> = Vec::with_capacity(num.len());
    for b in num.bytes() {
        // A bigger digit before a smaller one should go.
        while k > 0 && stack.last().is_some_and(|&top| top > b) {
            stack.pop();
            k -= 1;
        }
        stack.push(b);
    }
    // What's left is non-decreasing: drop any remaining removals from the end.
    stack.truncate(stack.len() - k);
    let start = stack.iter().position(|&b| b != b'0').unwrap_or(stack.len());
    match std::str::from_utf8(&stack[start..]).unwrap() {
        "" => "0".to_string(),
        digits => digits.to_string(),
    }
}
