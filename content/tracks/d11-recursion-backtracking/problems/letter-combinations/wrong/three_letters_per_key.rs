pub fn letter_combinations(digits: &str) -> Vec<String> {
    fn go(digits: &[u8], word: &mut String, out: &mut Vec<String>) {
        let Some((&d, rest)) = digits.split_first() else {
            out.push(word.clone());
            return;
        };
        let first = b'a' + 3 * (d - b'2');
        for c in first..first + 3 {
            word.push(c as char);
            go(rest, word, out);
            word.pop();
        }
    }
    let mut out = Vec::new();
    if !digits.is_empty() {
        go(digits.as_bytes(), &mut String::new(), &mut out);
    }
    out
}
