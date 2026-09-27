pub fn is_valid(s: &str) -> bool {
    let mut expected = Vec::new();
    for b in s.bytes() {
        match b {
            b'(' => expected.push(b')'),
            b'[' => expected.push(b']'),
            b'{' => expected.push(b'}'),
            _ => {
                if expected.pop() != Some(b) {
                    return false;
                }
            }
        }
    }
    true
}
