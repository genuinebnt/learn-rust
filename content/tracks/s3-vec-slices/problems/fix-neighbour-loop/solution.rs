/// Differences between neighbours: [a, b, c] → [b - a, c - b].
pub fn deltas(v: &[i64]) -> Vec<i64> {
    v.windows(2).map(|w| w[1] - w[0]).collect()
}

/// Indices of strict local peaks: v[i - 1] < v[i] > v[i + 1]. The two ends are never peaks.
pub fn peaks(v: &[i32]) -> Vec<usize> {
    v.windows(3).enumerate().filter(|(_, w)| w[0] < w[1] && w[1] > w[2]).map(|(i, _)| i + 1).collect()
}

/// The wrapping sum of the big-endian 16-bit words in `bytes`; an odd last byte is padded with a zero byte.
pub fn sum16(bytes: &[u8]) -> u16 {
    let words = bytes.chunks_exact(2);
    let tail = match words.remainder() {
        [last] => u16::from_be_bytes([*last, 0]),
        _ => 0,
    };
    words.fold(tail, |sum, w| sum.wrapping_add(u16::from_be_bytes([w[0], w[1]])))
}

/// Groups of three digits from the right, joined by commas: "1234567" → "1,234,567". `digits` is ASCII.
pub fn with_commas(digits: &str) -> String {
    digits.as_bytes().rchunks(3).rev().map(|c| std::str::from_utf8(c).unwrap()).collect::<Vec<_>>().join(",")
}
