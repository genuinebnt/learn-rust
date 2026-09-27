pub fn is_match(s: &str, p: &str) -> bool {
    let s: Vec<char> = s.chars().collect();
    let p: Vec<char> = p.chars().collect();
    // row[j] = whether the first i characters of s match the first j of p, for the current i.
    // With i = 0 only a run of leading '*'s matches.
    let mut row = vec![false; p.len() + 1];
    row[0] = true;
    for j in 1..=p.len() {
        row[j] = row[j - 1] && p[j - 1] == '*';
    }
    for &c in &s {
        let mut next = vec![false; p.len() + 1];
        for j in 1..=p.len() {
            next[j] = match p[j - 1] {
                // '*' matches nothing (next[j - 1]) or also takes c (row[j]).
                '*' => next[j - 1] || row[j],
                '?' => row[j - 1],
                q => row[j - 1] && q == c,
            };
        }
        row = next;
    }
    row[p.len()]
}
