pub fn palindrome_pairs(words: &[&str]) -> Vec<(usize, usize)> {
    let mut out = Vec::new();
    for i in 0..words.len() {
        for j in 0..words.len() {
            let s = format!("{}{}", words[i], words[j]);
            if i != j && s.bytes().eq(s.bytes().rev()) {
                out.push((i, j));
            }
        }
    }
    out
}
