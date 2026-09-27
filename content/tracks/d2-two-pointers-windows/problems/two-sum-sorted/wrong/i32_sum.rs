use std::cmp::Ordering;

pub fn two_sum_sorted(nums: &[i32], target: i32) -> Option<(usize, usize)> {
    let (mut l, mut r) = (0, nums.len().checked_sub(1)?);
    while l < r {
        match (nums[l] + nums[r]).cmp(&target) {
            Ordering::Equal => return Some((l, r)),
            Ordering::Less => l += 1,
            Ordering::Greater => r -= 1,
        }
    }
    None
}
