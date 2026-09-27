pub fn join_words(words: &[&str], sep: &str) -> String {
    let mut out = String::new();
    for (i, w) in words.iter().enumerate() {
        if i > 0 {
            out.push_str(sep);
        }
        out.push_str(w);
    }
    out
}
