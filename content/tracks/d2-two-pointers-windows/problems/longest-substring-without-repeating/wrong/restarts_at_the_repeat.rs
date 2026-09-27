pub fn length_of_longest_substring(s: &str) -> usize {
    let mut seen = [false; 256];
    let (mut len, mut best) = (0, 0);
    for b in s.bytes() {
        if seen[b as usize] {
            seen = [false; 256];
            len = 0;
        }
        seen[b as usize] = true;
        len += 1;
        best = best.max(len);
    }
    best
}
