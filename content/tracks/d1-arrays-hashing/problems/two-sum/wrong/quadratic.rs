pub fn two_sum(nums: &[i32], target: i32) -> Option<(usize, usize)> {
    for j in 0..nums.len() {
        for i in 0..j {
            if nums[i] + nums[j] == target {
                return Some((i, j));
            }
        }
    }
    None
}
