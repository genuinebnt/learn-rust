pub fn search(nums: &[i32], target: i32) -> Option<usize> {
    // Half-open [lo, hi): empty when lo == hi, and `hi - lo` never underflows.
    let (mut lo, mut hi) = (0, nums.len());
    while lo < hi {
        let mid = lo + (hi - lo) / 2;
        match nums[mid].cmp(&target) {
            std::cmp::Ordering::Less => lo = mid + 1,
            std::cmp::Ordering::Greater => hi = mid,
            std::cmp::Ordering::Equal => return Some(mid),
        }
    }
    None
}
