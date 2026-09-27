pub fn can_construct(note: &str, magazine: &str) -> bool {
    let mut have = [0u32; 26];
    for b in magazine.bytes() {
        have[(b - b'a') as usize] += 1;
    }
    for b in note.bytes() {
        let slot = &mut have[(b - b'a') as usize];
        if *slot == 0 {
            return false;
        }
        *slot -= 1;
    }
    true
}
