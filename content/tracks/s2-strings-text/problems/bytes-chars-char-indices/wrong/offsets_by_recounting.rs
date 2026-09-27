pub fn sizes(s: &str) -> (usize, usize) {
    (s.len(), s.chars().count())
}

pub fn positions(s: &str, target: char) -> Vec<usize> {
    let mut out = Vec::new();
    for (k, c) in s.chars().enumerate() {
        if c == target {
            out.push(s.chars().take(k).map(char::len_utf8).sum());
        }
    }
    out
}

pub fn nth_char(s: &str, n: usize) -> Option<char> {
    s.chars().nth(n)
}
