/// Lowercases `text` and joins its words with "-".
pub fn slug(text: &str) -> String {
    let s = text.split_whitespace().collect::<Vec<_>>().join("-").to_lowercase();
    s
}
