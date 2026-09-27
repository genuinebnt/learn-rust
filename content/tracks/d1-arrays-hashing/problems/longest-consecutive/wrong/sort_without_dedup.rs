pub fn longest_consecutive(nums: &[i32]) -> usize {
    let mut s = nums.to_vec();
    s.sort_unstable();
    let (mut best, mut run) = (0, 0);
    for i in 0..s.len() {
        run = if i > 0 && s[i] as i64 == s[i - 1] as i64 + 1 { run + 1 } else { 1 };
        best = best.max(run);
    }
    best
}
