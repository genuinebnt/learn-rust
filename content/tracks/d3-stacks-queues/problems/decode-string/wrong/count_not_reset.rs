pub fn decode_string(s: &str) -> String {
    let mut frames: Vec<(String, usize)> = Vec::new();
    let (mut current, mut k) = (String::new(), 0usize);
    for b in s.bytes() {
        match b {
            b'0'..=b'9' => k = k * 10 + usize::from(b - b'0'),
            b'[' => {
                frames.push((std::mem::take(&mut current), k));

            }
            b']' => {
                let (before, n) = frames.pop().expect("balanced brackets");
                current = before + &current.repeat(n);
            }
            _ => current.push(char::from(b)),
        }
    }
    current
}
