pub fn min_cut(s: &str) -> usize {
    let s = s.as_bytes();
    let n = s.len();
    let mut pieces: Vec<usize> = (0..=n).collect();
    for end in 1..=n {
        for start in 0..end {
            if s[start..end].iter().eq(s[start..end].iter().rev()) {
                pieces[end] = pieces[end].min(pieces[start] + 1);
            }
        }
    }
    pieces[n].saturating_sub(1)
}
