pub fn join_words(words: &[&str], sep: &str) -> String {
    let mut out = String::new();
    for (i, w) in words.iter().enumerate() {
        out = if i == 0 { w.to_string() } else { format!("{out}{sep}{w}") };
    }
    out.shrink_to_fit();
    out
}
