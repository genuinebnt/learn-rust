pub fn is_anagram(s: &str, t: &str) -> bool {
    let mut rest: Vec<u8> = t.bytes().collect();
    for b in s.bytes() {
        match rest.iter().position(|&c| c == b) {
            Some(i) => {
                rest.remove(i);
            }
            None => return false,
        }
    }
    rest.is_empty()
}
