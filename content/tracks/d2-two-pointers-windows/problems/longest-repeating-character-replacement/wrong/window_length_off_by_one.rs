pub fn character_replacement(s: &str, k: usize) -> usize {
    let b = s.as_bytes();
    let mut counts = [0usize; 26];
    let (mut start, mut most, mut best) = (0, 0, 0);
    for end in 0..b.len() {
        let c = (b[end] - b'A') as usize;
        counts[c] += 1;
        most = most.max(counts[c]);
        while end - start > most + k {
            counts[(b[start] - b'A') as usize] -= 1;
            start += 1;
        }
        best = best.max(end + 1 - start);
    }
    best
}
