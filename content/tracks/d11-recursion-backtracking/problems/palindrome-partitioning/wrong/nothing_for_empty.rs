pub fn partition(s: &str) -> Vec<Vec<&str>> {
    fn go<'a>(s: &'a str, start: usize, path: &mut Vec<&'a str>, out: &mut Vec<Vec<&'a str>>) {
        if start == s.len() {
            out.push(path.clone());
            return;
        }
        for end in start + 1..=s.len() {
            let piece = &s[start..end];
            if piece.bytes().eq(piece.bytes().rev()) {
                path.push(piece);
                go(s, end, path, out);
                path.pop();
            }
        }
    }
    if s.is_empty() {
        return Vec::new();
    }
    let mut out = Vec::new();
    go(s, 0, &mut Vec::new(), &mut out);
    out
}
