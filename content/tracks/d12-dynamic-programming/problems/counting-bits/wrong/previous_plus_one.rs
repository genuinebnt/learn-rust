pub fn count_bits(n: usize) -> Vec<u32> {
    let mut bits = vec![0u32; n + 1];
    for i in 1..=n {
        bits[i] = if i.is_power_of_two() { 1 } else { bits[i - 1] + 1 };
    }
    bits
}
