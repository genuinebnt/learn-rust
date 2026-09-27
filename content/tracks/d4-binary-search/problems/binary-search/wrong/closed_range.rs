pub fn search(nums: &[i32], target: i32) -> Option<usize> {
    let (mut lo, mut hi) = (0, nums.len() - 1);
    while lo <= hi {
        let mid = lo + (hi - lo) / 2;
        match nums[mid].cmp(&target) {
            std::cmp::Ordering::Less => lo = mid + 1,
            std::cmp::Ordering::Greater => hi = mid - 1,
            std::cmp::Ordering::Equal => return Some(mid),
        }
    }
    None
}
