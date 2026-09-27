pub fn is_match(s: &str, p: &str) -> bool {
    let s: Vec<char> = s.chars().collect();
    let p: Vec<char> = p.chars().collect();
    let (n, m) = (s.len(), p.len());
    // ok[i][j] = whether s[i..] matches p[j..]. An empty pattern matches only the empty rest.
    let mut ok = vec![vec![false; m + 1]; n + 1];
    ok[n][m] = true;
    for i in (0..=n).rev() {
        for j in (0..m).rev() {
            let first = i < n && (p[j] == '.' || p[j] == s[i]);
            ok[i][j] = if j + 1 < m && p[j + 1] == '*' {
                // Skip "x*" entirely, or let it eat s[i] and stay on the same unit.
                ok[i][j + 2] || (first && ok[i + 1][j])
            } else {
                first && ok[i + 1][j + 1]
            };
        }
    }
    ok[0][0]
}
