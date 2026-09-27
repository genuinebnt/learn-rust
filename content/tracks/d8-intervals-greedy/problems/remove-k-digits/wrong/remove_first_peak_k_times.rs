pub fn remove_kdigits(num: &str, k: usize) -> String {
    let mut digits: Vec<u8> = num.bytes().collect();
    for _ in 0..k {
        let i = (0..digits.len() - 1).find(|&i| digits[i] > digits[i + 1]).unwrap_or(digits.len() - 1);
        digits.remove(i);
    }
    let s: String = digits.iter().map(|&b| b as char).collect();
    let s = s.trim_start_matches('0');
    if s.is_empty() { "0".to_string() } else { s.to_string() }
}
