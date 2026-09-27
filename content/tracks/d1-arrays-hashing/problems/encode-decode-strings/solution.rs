/// Each word as `<byte length>#<word>`.
pub fn encode(words: &[&str]) -> String {
    let mut out = String::new();
    for w in words {
        out.push_str(&w.len().to_string());
        out.push('#');
        out.push_str(w);
    }
    out
}

pub fn decode(s: &str) -> Vec<String> {
    let mut out = Vec::new();
    let mut rest = s;
    while let Some(hash) = rest.find('#') {
        let len: usize = rest[..hash].parse().expect("length prefix");
        let start = hash + 1;
        out.push(rest[start..start + len].to_string());
        rest = &rest[start + len..];
    }
    out
}
