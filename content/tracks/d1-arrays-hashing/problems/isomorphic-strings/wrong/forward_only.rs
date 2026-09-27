pub fn is_isomorphic(s: &str, t: &str) -> bool {
    let mut forward: [Option<u8>; 256] = [None; 256];
    for (a, b) in s.bytes().zip(t.bytes()) {
        match forward[a as usize] {
            None => forward[a as usize] = Some(b),
            Some(x) if x == b => {}
            Some(_) => return false,
        }
    }
    true
}
