pub fn two_sum_sorted(nums: &[i32], target: i32) -> Option<(usize, usize)> {
    for i in 0..nums.len() {
        for j in i + 1..nums.len() {
            if nums[i] as i64 + nums[j] as i64 == target as i64 {
                return Some((i, j));
            }
        }
    }
    None
}
