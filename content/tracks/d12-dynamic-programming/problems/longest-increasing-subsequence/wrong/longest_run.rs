pub fn length_of_lis(nums: &[i32]) -> usize {
    let (mut run, mut best) = (0, 0);
    for i in 0..nums.len() {
        run = if i > 0 && nums[i - 1] < nums[i] { run + 1 } else { 1 };
        best = best.max(run);
    }
    best
}
