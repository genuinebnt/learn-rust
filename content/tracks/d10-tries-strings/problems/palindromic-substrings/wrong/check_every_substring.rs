pub fn count_substrings(s: &str) -> usize {
    let chars: Vec<char> = s.chars().collect();
    let mut count = 0;
    for i in 0..chars.len() {
        for j in i + 1..=chars.len() {
            let w = &chars[i..j];
            count += w.iter().eq(w.iter().rev()) as usize;
        }
    }
    count
}
