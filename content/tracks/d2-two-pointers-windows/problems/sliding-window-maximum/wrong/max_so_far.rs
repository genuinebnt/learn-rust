pub fn max_sliding_window(nums: &[i32], k: usize) -> Vec<i32> {
    let mut best = i32::MIN;
    let mut out = Vec::new();
    for (i, &x) in nums.iter().enumerate() {
        best = best.max(x);
        if i + 1 >= k {
            out.push(best);
        }
    }
    out
}
