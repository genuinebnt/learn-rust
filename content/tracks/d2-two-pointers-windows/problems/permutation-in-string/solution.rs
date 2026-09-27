pub fn check_inclusion(pattern: &str, s: &str) -> bool {
    let (p, s) = (pattern.as_bytes(), s.as_bytes());
    if p.len() > s.len() {
        return false;
    }
    let idx = |b: u8| (b - b'a') as usize;
    let (mut want, mut have) = ([0u32; 26], [0u32; 26]);
    for &b in p {
        want[idx(b)] += 1;
    }
    for (i, &b) in s.iter().enumerate() {
        have[idx(b)] += 1;
        if i >= p.len() {
            have[idx(s[i - p.len()])] -= 1;
        }
        if have == want {
            return true;
        }
    }
    false
}
