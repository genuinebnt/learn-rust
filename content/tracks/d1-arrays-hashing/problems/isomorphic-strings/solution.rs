pub fn is_isomorphic(s: &str, t: &str) -> bool {
    let mut forward: [Option<u8>; 256] = [None; 256];
    let mut backward: [Option<u8>; 256] = [None; 256];
    for (a, b) in s.bytes().zip(t.bytes()) {
        match (forward[a as usize], backward[b as usize]) {
            (None, None) => {
                forward[a as usize] = Some(b);
                backward[b as usize] = Some(a);
            }
            (Some(x), Some(y)) if x == b && y == a => {}
            _ => return false,
        }
    }
    true
}
