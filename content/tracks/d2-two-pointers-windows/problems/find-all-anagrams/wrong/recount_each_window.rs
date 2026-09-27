pub fn find_anagrams(s: &str, p: &str) -> Vec<usize> {
    let (s, p) = (s.as_bytes(), p.as_bytes());
    if p.is_empty() || p.len() > s.len() {
        return Vec::new();
    }
    let mut want = [0u32; 26];
    for &b in p {
        want[(b - b'a') as usize] += 1;
    }
    (0..=s.len() - p.len())
        .filter(|&i| {
            let mut have = [0u32; 26];
            for &b in &s[i..i + p.len()] {
                have[(b - b'a') as usize] += 1;
            }
            have == want
        })
        .collect()
}
