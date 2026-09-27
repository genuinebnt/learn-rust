pub fn find_min(nums: &[i32]) -> Option<i32> {
    let last = *nums.last()?;
    // Everything before the minimum is greater than the last element; everything from it on isn't.
    Some(nums[nums.partition_point(|&x| x > last)])
}
