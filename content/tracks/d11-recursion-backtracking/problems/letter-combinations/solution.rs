const KEYS: [&str; 10] = ["", "", "abc", "def", "ghi", "jkl", "mno", "pqrs", "tuv", "wxyz"];

pub fn letter_combinations(digits: &str) -> Vec<String> {
    fn go(digits: &[u8], word: &mut String, out: &mut Vec<String>) {
        let Some((&d, rest)) = digits.split_first() else {
            out.push(word.clone());
            return;
        };
        for c in KEYS[(d - b'0') as usize].chars() {
            word.push(c);
            go(rest, word, out);
            word.pop();
        }
    }
    let mut out = Vec::new();
    if !digits.is_empty() {
        go(digits.as_bytes(), &mut String::with_capacity(digits.len()), &mut out);
    }
    out
}
