pub fn contains_duplicate(nums: &[i32]) -> bool {
    (0..nums.len()).any(|i| nums[i + 1..].contains(&nums[i]))
}
