pub fn can_construct(note: &str, magazine: &str) -> bool {
    note.bytes().all(|b| magazine.as_bytes().contains(&b))
}
