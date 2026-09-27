use std::collections::HashMap;

fn code(b: u8) -> u64 {
    match b {
        b'A' => 0,
        b'C' => 1,
        b'G' => 2,
        _ => 3,
    }
}

pub fn find_repeated_dna_sequences(s: &str, k: usize) -> Vec<&str> {
    let b = s.as_bytes();
    if k > b.len() {
        return Vec::new();
    }
    // The window as a base-4 number. 4^k ≤ 2^64 for k ≤ 32, so different windows get different keys.
    let top = 4u64.pow(k as u32 - 1); // weight of the window's first letter
    let mut key = 0u64;
    // key -> (where it first starts, how many times it was seen)
    let mut seen: HashMap<u64, (usize, u32)> = HashMap::new();
    for i in 0..b.len() {
        if i >= k {
            key -= code(b[i - k]) * top;
        }
        key = key * 4 + code(b[i]);
        if i + 1 >= k {
            seen.entry(key).or_insert((i + 1 - k, 0)).1 += 1;
        }
    }
    let mut starts: Vec<usize> = seen.into_values().filter(|&(_, n)| n >= 2).map(|(start, _)| start).collect();
    starts.sort_unstable();
    starts.into_iter().map(|i| &s[i..i + k]).collect()
}
