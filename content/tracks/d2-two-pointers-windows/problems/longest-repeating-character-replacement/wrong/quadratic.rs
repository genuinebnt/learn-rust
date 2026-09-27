pub fn character_replacement(s: &str, k: usize) -> usize {
    let b = s.as_bytes();
    let mut best = 0;
    for start in 0..b.len() {
        let mut counts = [0usize; 26];
        let mut most = 0;
        for end in start..b.len() {
            let c = (b[end] - b'A') as usize;
            counts[c] += 1;
            most = most.max(counts[c]);
            if end + 1 - start - most > k {
                break;
            }
            best = best.max(end + 1 - start);
        }
    }
    best
}
