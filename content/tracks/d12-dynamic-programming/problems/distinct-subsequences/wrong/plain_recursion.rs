fn count(s: &[u8], t: &[u8]) -> u64 {
    match (s, t) {
        (_, []) => 1,
        ([], _) => 0,
        ([x, rs @ ..], [y, rt @ ..]) => count(rs, t) + if x == y { count(rs, rt) } else { 0 },
    }
}

pub fn num_distinct(s: &str, t: &str) -> u64 {
    count(s.as_bytes(), t.as_bytes())
}
