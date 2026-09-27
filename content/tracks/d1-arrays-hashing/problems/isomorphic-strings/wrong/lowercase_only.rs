pub fn is_isomorphic(s: &str, t: &str) -> bool {
    let mut forward: [Option<u8>; 26] = [None; 26];
    let mut backward: [Option<u8>; 26] = [None; 26];
    for (a, b) in s.bytes().zip(t.bytes()) {
        let (i, j) = ((a - b'a') as usize, (b - b'a') as usize);
        match (forward[i], backward[j]) {
            (None, None) => {
                forward[i] = Some(b);
                backward[j] = Some(a);
            }
            (Some(x), Some(y)) if x == b && y == a => {}
            _ => return false,
        }
    }
    true
}
