pub fn encode(words: &[&str]) -> String {
    words.join("#")
}

pub fn decode(s: &str) -> Vec<String> {
    if s.is_empty() {
        return Vec::new();
    }
    s.split('#').map(String::from).collect()
}
