pub fn count_bits(n: usize) -> Vec<u32> {
    let mut bits = vec![0u32; n + 1];
    for i in 1..=n {
        // i >> 1 drops the lowest bit; add it back.
        bits[i] = bits[i >> 1] + (i & 1) as u32;
    }
    bits
}
