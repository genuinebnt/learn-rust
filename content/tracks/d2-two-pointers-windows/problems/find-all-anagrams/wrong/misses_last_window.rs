pub fn find_anagrams(s: &str, p: &str) -> Vec<usize> {
    let (s, p) = (s.as_bytes(), p.as_bytes());
    let mut out = Vec::new();
    if p.is_empty() || p.len() > s.len() {
        return out;
    }
    let idx = |b: u8| (b - b'a') as usize;
    let (mut want, mut have) = ([0u32; 26], [0u32; 26]);
    for &b in p {
        want[idx(b)] += 1;
    }
    for &b in &s[..p.len()] {
        have[idx(b)] += 1;
    }
    for i in p.len()..s.len() {
        if have == want {
            out.push(i - p.len());
        }
        have[idx(s[i])] += 1;
        have[idx(s[i - p.len()])] -= 1;
    }
    out
}
