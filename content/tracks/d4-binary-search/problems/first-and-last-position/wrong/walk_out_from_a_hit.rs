pub fn search_range(nums: &[i32], target: i32) -> Option<(usize, usize)> {
    let hit = nums.binary_search(&target).ok()?;
    let (mut start, mut end) = (hit, hit);
    while start > 0 && nums[start - 1] == target {
        start -= 1;
    }
    while end + 1 < nums.len() && nums[end + 1] == target {
        end += 1;
    }
    Some((start, end))
}
