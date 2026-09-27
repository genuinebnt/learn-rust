pub fn decode_string(s: &str) -> String {
    let mut s = s.to_string();
    while let Some(close) = s.find(']') {
        let open = s[..close].rfind('[').expect("balanced brackets");
        let start = s[..open].rfind(|c: char| !c.is_ascii_digit()).map_or(0, |i| i + 1);
        let k: usize = s[start..open].parse().expect("a count before '['");
        let inner = s[open + 1..close].repeat(k);
        s.replace_range(start..=close, &inner);
    }
    s
}
