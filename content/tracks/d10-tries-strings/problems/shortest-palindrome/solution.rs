pub fn shortest_palindrome(s: &str) -> String {
    let chars: Vec<char> = s.chars().collect();
    // s, a separator equal to no character (None), then s reversed.
    let t: Vec<Option<char>> = chars.iter().copied().map(Some).chain([None]).chain(chars.iter().rev().copied().map(Some)).collect();
    // KMP border table of t.
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
    // The longest prefix of s that is also a suffix of reverse(s): the longest palindromic prefix.
    let keep = border[t.len() - 1];
    chars[keep..].iter().rev().chain(&chars).collect()
}
