/// Pushes `x` and returns the largest value, which may be `x`.
pub fn add_and_max(v: &mut Vec<i32>, x: i32) -> i32 {
    let max = v.last().copied().unwrap_or(x);
    v.push(x);
    max.max(x)
}
