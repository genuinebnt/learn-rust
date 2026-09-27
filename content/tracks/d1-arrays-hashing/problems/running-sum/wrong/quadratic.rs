pub fn running_sum(nums: &[i32]) -> Vec<i32> {
    (0..nums.len()).map(|i| nums[..=i].iter().sum()).collect()
}
