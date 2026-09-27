pub fn min_cut(s: &str) -> usize {
    let s = s.as_bytes();
    let (mut start, mut pieces) = (0, 0usize);
    while start < s.len() {
        let end = (start + 1..=s.len()).rev().find(|&e| s[start..e].iter().eq(s[start..e].iter().rev())).unwrap();
        start = end;
        pieces += 1;
    }
    pieces.saturating_sub(1)
}
