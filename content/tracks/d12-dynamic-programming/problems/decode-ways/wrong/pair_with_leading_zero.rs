pub fn num_decodings(s: &str) -> u64 {
    let d = s.as_bytes();
    let (mut two_back, mut one_back) = (0u64, 1u64);
    for i in 0..d.len() {
        let mut here = 0;
        if d[i] != b'0' {
            here += one_back;
        }
        if i > 0 && (1..=26).contains(&((d[i - 1] - b'0') * 10 + (d[i] - b'0'))) {
            here += two_back;
        }
        (two_back, one_back) = (one_back, here);
    }
    one_back
}
