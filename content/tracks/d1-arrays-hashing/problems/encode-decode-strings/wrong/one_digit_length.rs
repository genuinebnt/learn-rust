pub fn encode(words: &[&str]) -> String {
    words.iter().map(|w| format!("{}#{}", w.len() % 10, w)).collect()
}

pub fn decode(s: &str) -> Vec<String> {
    let mut out = Vec::new();
    let mut rest = s;
    while !rest.is_empty() {
        let len = (rest.as_bytes()[0] - b'0') as usize;
        out.push(rest[2..2 + len].to_string());
        rest = &rest[2 + len..];
    }
    out
}
