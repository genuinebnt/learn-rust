pub fn join_words(words: &[&str], sep: &str) -> String {
    let len = words.iter().map(|w| w.len() + sep.len()).sum::<usize>();
    let mut out = String::with_capacity(len);
    for w in words {
        out.push_str(w);
        out.push_str(sep);
    }
    out
}
