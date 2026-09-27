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
    stack.truncate(stack.len() - k);
    if stack.is_empty() { "0".to_string() } else { String::from_utf8(stack).unwrap() }
}
