/// Sums of neighbouring pairs: [a, b, c] → [a + b, b + c].
pub fn pair_sums(v: &[i32]) -> Vec<i32> {
    let mut out = Vec::new();
    for i in 0..v.len() {
        out.push(v[i] + v[i + 1]);
    }
    out
}
