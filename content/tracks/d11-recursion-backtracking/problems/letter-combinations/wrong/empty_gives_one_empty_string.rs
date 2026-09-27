const KEYS: [&str; 10] = ["", "", "abc", "def", "ghi", "jkl", "mno", "pqrs", "tuv", "wxyz"];

pub fn letter_combinations(digits: &str) -> Vec<String> {
    let mut out = vec![String::new()];
    for d in digits.bytes() {
        out = out.iter().flat_map(|w| KEYS[(d - b'0') as usize].chars().map(move |c| format!("{w}{c}"))).collect();
    }
    out
}
