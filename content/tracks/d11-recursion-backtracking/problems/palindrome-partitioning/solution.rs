pub fn partition(s: &str) -> Vec<Vec<&str>> {
    fn go<'a>(s: &'a str, start: usize, pal: &[Vec<bool>], path: &mut Vec<&'a str>, out: &mut Vec<Vec<&'a str>>) {
        if start == s.len() {
            out.push(path.clone());
            return;
        }
        for end in start + 1..=s.len() {
            if pal[start][end - 1] {
                path.push(&s[start..end]);
                go(s, end, pal, path, out);
                path.pop();
            }
        }
    }
    let (b, n) = (s.as_bytes(), s.len());
    // pal[i][j]: s[i..=j] is a palindrome. Row i reads row i + 1, so fill from the bottom.
    let mut pal = vec![vec![false; n]; n];
    for i in (0..n).rev() {
        for j in i..n {
            pal[i][j] = b[i] == b[j] && (j - i < 2 || pal[i + 1][j - 1]);
        }
    }
    let mut out = Vec::new();
    go(s, 0, &pal, &mut Vec::new(), &mut out);
    out
}
