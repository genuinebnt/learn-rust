pub fn num_distinct(s: &str, t: &str) -> u64 {
    let t = t.as_bytes();
    let mut ways = vec![0u64; t.len() + 1];
    ways[0] = 1;
    for &c in s.as_bytes() {
        for j in 1..=t.len() {
            if t[j - 1] == c {
                ways[j] = ways[j].wrapping_add(ways[j - 1]);
            }
        }
    }
    ways[t.len()]
}
