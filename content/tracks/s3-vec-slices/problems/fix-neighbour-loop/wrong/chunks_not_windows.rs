/// Sums of neighbouring pairs: [a, b, c] → [a + b, b + c].
pub fn pair_sums(v: &[i32]) -> Vec<i32> {
    v.chunks(2).map(|c| c.iter().sum()).collect()
}
