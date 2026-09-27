pub fn can_partition_k_subsets(nums: &[u32], k: usize) -> bool {
    fn fill(nums: &[u32], target: u32, used: &mut [bool], k: usize, open: u32, start: usize) -> bool {
        if k == 1 {
            return true;
        }
        if open == target {
            return fill(nums, target, used, k - 1, 0, 0);
        }
        for i in start..nums.len() {
            if used[i] || open + nums[i] > target {
                continue;
            }
            used[i] = true;
            if fill(nums, target, used, k, open + nums[i], i + 1) {
                return true;
            }
            used[i] = false;
        }
        false
    }
    let total: u32 = nums.iter().sum();
    if total % k as u32 != 0 {
        return false;
    }
    let target = total / k as u32;
    let mut nums = nums.to_vec();
    nums.sort_unstable_by(|a, b| b.cmp(a));
    nums[0] <= target && fill(&nums, target, &mut vec![false; nums.len()], k, 0, 0)
}
