/// Differences between neighbours: [a, b, c] → [b - a, c - b].
pub fn deltas(v: &[i64]) -> Vec<i64> {
    let mut out = Vec::new();
    for i in 0..v.len() - 1 {
        out.push(v[i + 1] - v[i]);
    }
    out
}

/// Indices of strict local peaks: v[i - 1] < v[i] > v[i + 1]. The two ends are never peaks.
pub fn peaks(v: &[i32]) -> Vec<usize> {
    let mut out = Vec::new();
    for i in 1..v.len() {
        if v[i - 1] < v[i] && v[i] > v[i + 1] {
            out.push(i);
        }
    }
    out
}

/// The wrapping sum of the big-endian 16-bit words in `bytes`; an odd last byte is padded with a zero byte.
pub fn sum16(bytes: &[u8]) -> u16 {
    let mut sum = 0u16;
    for i in (0..bytes.len()).step_by(2) {
        sum = sum.wrapping_add(u16::from_be_bytes([bytes[i], bytes[i + 1]]));
    }
    sum
}

/// Groups of three digits from the right, joined by commas: "1234567" → "1,234,567". `digits` is ASCII.
pub fn with_commas(digits: &str) -> String {
    digits.as_bytes().chunks(3).map(|c| std::str::from_utf8(c).unwrap()).collect::<Vec<_>>().join(",")
}
