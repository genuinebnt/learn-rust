pub fn check_inclusion(pattern: &str, s: &str) -> bool {
    let (p, s) = (pattern.as_bytes(), s.as_bytes());
    if p.len() > s.len() {
        return false;
    }
    let mut want = [0u32; 26];
    for &b in p {
        want[(b - b'a') as usize] += 1;
    }
    (0..=s.len() - p.len()).any(|i| {
        let mut have = [0u32; 26];
        for &b in &s[i..i + p.len()] {
            have[(b - b'a') as usize] += 1;
        }
        have == want
    })
}
