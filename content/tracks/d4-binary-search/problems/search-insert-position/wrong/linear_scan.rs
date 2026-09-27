pub fn insert_position(nums: &[i32], target: i32) -> usize {
    nums.iter().position(|&x| x >= target).unwrap_or(nums.len())
}
