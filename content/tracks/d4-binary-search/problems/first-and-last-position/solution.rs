pub fn search_range(nums: &[i32], target: i32) -> Option<(usize, usize)> {
    let start = nums.partition_point(|&x| x < target);
    let end = nums.partition_point(|&x| x <= target);
    (start < end).then(|| (start, end - 1))
}
