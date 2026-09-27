pub fn search_rotated(nums: &[i32], target: i32) -> Option<usize> {
    nums.iter().position(|&x| x == target)
}
