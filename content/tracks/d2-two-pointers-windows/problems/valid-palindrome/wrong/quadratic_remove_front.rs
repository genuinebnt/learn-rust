pub fn is_palindrome(s: &str) -> bool {
    let mut kept: Vec<u8> = s.bytes().filter(|b| b.is_ascii_alphanumeric()).map(|b| b.to_ascii_lowercase()).collect();
    while kept.len() > 1 {
        let first = kept[0];
        for i in 1..kept.len() {
            kept[i - 1] = kept[i];
        }
        kept.pop();
        if kept.pop() != Some(first) {
            return false;
        }
    }
    true
}
