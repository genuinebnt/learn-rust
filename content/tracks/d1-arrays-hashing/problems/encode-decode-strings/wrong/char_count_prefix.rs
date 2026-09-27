pub fn encode(words: &[&str]) -> String {
    words.iter().map(|w| format!("{}#{}", w.chars().count(), w)).collect()
}

pub fn decode(s: &str) -> Vec<String> {
    let mut out = Vec::new();
    let mut rest = s;
    while let Some(hash) = rest.find('#') {
        let len: usize = rest[..hash].parse().expect("length prefix");
        let word: String = rest[hash + 1..].chars().take(len).collect();
        rest = &rest[hash + 1 + len..];
        out.push(word);
    }
    out
}
