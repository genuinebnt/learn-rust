pub fn find_min(nums: &[i32]) -> Option<i32> {
    if nums.is_empty() {
        return None;
    }
    let (mut lo, mut hi) = (0, nums.len() - 1);
    while lo < hi {
        let mid = lo + (hi - lo) / 2;
        if nums[mid] > nums[lo] {
            lo = mid + 1;
        } else {
            hi = mid;
        }
    }
    Some(nums[lo])
}
