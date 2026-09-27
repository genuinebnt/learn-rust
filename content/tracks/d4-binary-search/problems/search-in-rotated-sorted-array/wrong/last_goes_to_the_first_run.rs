pub fn search_rotated(nums: &[i32], target: i32) -> Option<usize> {
    let last = *nums.last()?;
    let pivot = nums.partition_point(|&x| x > last);
    let (high, low) = nums.split_at(pivot);
    if target >= last {
        high.binary_search(&target).ok()
    } else {
        low.binary_search(&target).ok().map(|i| i + pivot)
    }
}
