pub fn insert_position(nums: &[i32], target: i32) -> usize {
    nums.partition_point(|&x| x <= target)
}
