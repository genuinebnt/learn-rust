pub fn check_inclusion(pattern: &str, s: &str) -> bool {
    let (p, s) = (pattern.as_bytes(), s.as_bytes());
    if p.len() > s.len() {
        return false;
    }
    let mut want = [false; 26];
    for &b in p {
        want[(b - b'a') as usize] = true;
    }
    s.windows(p.len()).any(|w| {
        let mut have = [false; 26];
        for &b in w {
            have[(b - b'a') as usize] = true;
        }
        have == want
    })
}
