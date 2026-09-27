use std::collections::HashMap;

pub fn find_repeated_dna_sequences(s: &str, k: usize) -> Vec<&str> {
    let b = s.as_bytes();
    if k > b.len() {
        return Vec::new();
    }
    let mask = (1u64 << (2 * k)) - 1;
    let mut key = 0u64;
    let mut seen: HashMap<u64, (usize, u32)> = HashMap::new();
    for i in 0..b.len() {
        let c = match b[i] {
            b'A' => 0,
            b'C' => 1,
            b'G' => 2,
            _ => 3,
        };
        key = ((key << 2) | c) & mask;
        if i + 1 >= k {
            seen.entry(key).or_insert((i + 1 - k, 0)).1 += 1;
        }
    }
    let mut starts: Vec<usize> = seen.into_values().filter(|&(_, n)| n >= 2).map(|(start, _)| start).collect();
    starts.sort_unstable();
    starts.into_iter().map(|i| &s[i..i + k]).collect()
}
