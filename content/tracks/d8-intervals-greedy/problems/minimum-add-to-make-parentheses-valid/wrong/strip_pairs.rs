pub fn min_add_to_make_valid(s: &str) -> usize {
    let mut rest: Vec<u8> = s.bytes().collect();
    while let Some(i) = rest.windows(2).position(|w| w[0] == b'(' && w[1] == b')') {
        rest.drain(i..i + 2);
    }
    rest.len()
}
