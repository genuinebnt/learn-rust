pub fn num_decodings(s: &str) -> u64 {
    let d = s.as_bytes();
    let (mut two_back, mut one_back) = (0u64, 1u64);
    for i in 0..d.len() {
        let mut here = one_back;
        if i > 0 && (d[i - 1] == b'1' || (d[i - 1] == b'2' && d[i] <= b'6')) {
            here += two_back;
        }
        (two_back, one_back) = (one_back, here);
    }
    one_back
}
