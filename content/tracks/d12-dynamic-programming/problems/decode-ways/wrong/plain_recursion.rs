fn count(d: &[u8]) -> u64 {
    if d.is_empty() {
        return 1;
    }
    let mut n = 0;
    if d[0] != b'0' {
        n += count(&d[1..]);
        if d.len() >= 2 && (d[0] - b'0') * 10 + (d[1] - b'0') <= 26 {
            n += count(&d[2..]);
        }
    }
    n
}

pub fn num_decodings(s: &str) -> u64 {
    count(s.as_bytes())
}
