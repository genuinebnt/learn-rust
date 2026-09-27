pub fn count_bits(n: usize) -> Vec<u32> {
    (0..n.max(1)).map(|i| i.count_ones()).collect()
}
