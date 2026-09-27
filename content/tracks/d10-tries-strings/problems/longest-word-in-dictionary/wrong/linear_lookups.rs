pub fn longest_word<'a>(words: &[&'a str]) -> &'a str {
    let mut best = "";
    for &w in words {
        if (1..=w.len()).all(|k| words.contains(&&w[..k])) && (w.len() > best.len() || (w.len() == best.len() && w < best)) {
            best = w;
        }
    }
    best
}
