pub fn remove_kdigits(num: &str, k: usize) -> String {
    let mut k = k;
    let mut stack: Vec<u8> = Vec::new();
    for b in num.bytes() {
        while k > 0 && stack.last().is_some_and(|&top| top > b) {
            stack.pop();
            k -= 1;
        }
        stack.push(b);
    }
    let start = stack.iter().position(|&b| b != b'0').unwrap_or(stack.len());
    match std::str::from_utf8(&stack[start..]).unwrap() {
        "" => "0".to_string(),
        digits => digits.to_string(),
    }
}
