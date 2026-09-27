pub fn reverse_each_word(s: &str) -> String {
    s.split_whitespace()
        .map(|w| String::from_utf8_lossy(&w.bytes().rev().collect::<Vec<u8>>()).into_owned())
        .collect::<Vec<_>>()
        .join(" ")
}
