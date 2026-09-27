pub fn can_construct(note: &str, magazine: &str) -> bool {
    let mut have: Vec<u8> = magazine.bytes().collect();
    for b in note.bytes() {
        match have.iter().position(|&c| c == b) {
            Some(i) => {
                have.remove(i);
            }
            None => return false,
        }
    }
    true
}
