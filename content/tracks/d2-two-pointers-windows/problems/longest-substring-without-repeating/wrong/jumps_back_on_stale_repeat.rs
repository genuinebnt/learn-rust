pub fn length_of_longest_substring(s: &str) -> usize {
    let mut last: [Option<usize>; 256] = [None; 256];
    let (mut start, mut best) = (0, 0);
    for (i, b) in s.bytes().enumerate() {
        if let Some(prev) = last[b as usize] {
            start = prev + 1;
        }
        last[b as usize] = Some(i);
        best = best.max(i + 1 - start);
    }
    best
}
