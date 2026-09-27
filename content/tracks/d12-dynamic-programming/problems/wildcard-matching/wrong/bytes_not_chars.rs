pub fn is_match(s: &str, p: &str) -> bool {
    let s = s.as_bytes();
    let p = p.as_bytes();
    let mut row = vec![false; p.len() + 1];
    row[0] = true;
    for j in 1..=p.len() {
        row[j] = row[j - 1] && p[j - 1] == b'*';
    }
    for &c in s {
        let mut next = vec![false; p.len() + 1];
        for j in 1..=p.len() {
            next[j] = match p[j - 1] {
                b'*' => next[j - 1] || row[j],
                b'?' => row[j - 1],
                q => row[j - 1] && q == c,
            };
        }
        row = next;
    }
    row[p.len()]
}
