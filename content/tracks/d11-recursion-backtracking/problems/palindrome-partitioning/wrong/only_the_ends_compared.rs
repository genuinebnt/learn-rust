pub fn partition(s: &str) -> Vec<Vec<&str>> {
    fn go<'a>(s: &'a str, start: usize, path: &mut Vec<&'a str>, out: &mut Vec<Vec<&'a str>>) {
        if start == s.len() {
            out.push(path.clone());
            return;
        }
        let b = s.as_bytes();
        for end in start + 1..=s.len() {
            if b[start] == b[end - 1] {
                path.push(&s[start..end]);
                go(s, end, path, out);
                path.pop();
            }
        }
    }
    let mut out = Vec::new();
    go(s, 0, &mut Vec::new(), &mut out);
    out
}
