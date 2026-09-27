/// Sums of neighbouring pairs: [a, b, c] → [a + b, b + c].
pub fn pair_sums(v: &[i32]) -> Vec<i32> {
    v.windows(2).map(|w| w[0] + w[1]).collect()
}
