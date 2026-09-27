pub fn longest_palindrome(s: &str) -> &str {
    let chars: Vec<char> = s.chars().collect();
    let offsets: Vec<usize> = s.char_indices().map(|(i, _)| i).chain([s.len()]).collect();
    let (mut lo, mut hi) = (0, 0);
    for i in 0..chars.len() {
        for j in i + 1..=chars.len() {
            let w = &chars[i..j];
            if w.iter().eq(w.iter().rev()) && j - i > hi - lo {
                (lo, hi) = (i, j);
            }
        }
    }
    &s[offsets[lo]..offsets[hi]]
}
