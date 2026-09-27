pub fn can_partition_k_subsets(nums: &[u32], k: usize) -> bool {
    let total: u32 = nums.iter().sum();
    if total % k as u32 != 0 {
        return false;
    }
    let target = total / k as u32;
    let mut nums = nums.to_vec();
    nums.sort_unstable_by(|a, b| b.cmp(a));
    let mut groups = vec![0u32; k];
    for x in nums {
        match groups.iter_mut().find(|g| **g + x <= target) {
            Some(g) => *g += x,
            None => return false,
        }
    }
    true
}
