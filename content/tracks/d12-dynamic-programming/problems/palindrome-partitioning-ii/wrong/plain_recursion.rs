fn fewest_pieces(s: &[u8]) -> usize {
    if s.is_empty() {
        return 0;
    }
    (1..=s.len()).filter(|&k| s[..k].iter().eq(s[..k].iter().rev())).map(|k| 1 + fewest_pieces(&s[k..])).min().unwrap()
}

pub fn min_cut(s: &str) -> usize {
    fewest_pieces(s.as_bytes()).saturating_sub(1)
}
