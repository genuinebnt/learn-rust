pub fn length_of_longest_substring(s: &str) -> usize {
    let mut last: [Option<usize>; 26] = [None; 26];
    let (mut start, mut best) = (0, 0);
    for (i, b) in s.bytes().enumerate() {
        let c = (b.to_ascii_lowercase() % 26) as usize;
        if let Some(prev) = last[c].filter(|&p| p >= start) {
            start = prev + 1;
        }
        last[c] = Some(i);
        best = best.max(i + 1 - start);
    }
    best
}
