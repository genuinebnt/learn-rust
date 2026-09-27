pub fn num_decodings(s: &str) -> u64 {
    let d = s.as_bytes();
    // ways(i) = decodings of the first i digits; keep ways(i - 2) and ways(i - 1).
    let (mut two_back, mut one_back) = (0u64, 1u64);
    for i in 0..d.len() {
        let mut here = 0;
        if d[i] != b'0' {
            here += one_back; // d[i] alone is a letter
        }
        if i > 0 && (d[i - 1] == b'1' || (d[i - 1] == b'2' && d[i] <= b'6')) {
            here += two_back; // d[i - 1..=i] is 10..=26
        }
        (two_back, one_back) = (one_back, here);
    }
    one_back
}
