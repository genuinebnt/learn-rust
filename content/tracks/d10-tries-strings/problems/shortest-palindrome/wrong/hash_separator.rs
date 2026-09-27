pub fn shortest_palindrome(s: &str) -> String {
    let chars: Vec<char> = s.chars().collect();
    let t: Vec<char> = chars.iter().copied().chain(['#']).chain(chars.iter().rev().copied()).collect();
    let mut border = vec![0; t.len()];
    let mut k = 0;
    for i in 1..t.len() {
        while k > 0 && t[i] != t[k] {
            k = border[k - 1];
        }
        if t[i] == t[k] {
            k += 1;
        }
        border[i] = k;
    }
    let keep = border[t.len() - 1].min(chars.len());
    chars[keep..].iter().rev().chain(&chars).collect()
}
