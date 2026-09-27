pub fn contains_duplicate(nums: &[i32]) -> bool {
    nums.windows(2).any(|w| w[0] == w[1])
}
