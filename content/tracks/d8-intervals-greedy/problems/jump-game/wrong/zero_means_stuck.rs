pub fn can_jump(nums: &[u32]) -> bool {
    nums[..nums.len() - 1].iter().all(|&j| j > 0)
}
