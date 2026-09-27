pub fn reorganize(s: &str) -> Option<String> {
    let mut counts = [0usize; 256];
    for b in s.bytes() {
        counts[b as usize] += 1;
    }
    let mut out: Vec<u8> = Vec::with_capacity(s.len());
    let mut last: Option<u8> = None;
    for _ in 0..s.len() {
        let pick = (0..256).filter(|&b| counts[b] > 0 && Some(b as u8) != last).max_by_key(|&b| counts[b])?;
        counts[pick] -= 1;
        out.push(pick as u8);
        last = Some(pick as u8);
    }
    Some(String::from_utf8_lossy(&out).into_owned())
}
