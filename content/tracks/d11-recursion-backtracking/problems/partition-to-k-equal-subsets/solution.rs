pub fn can_partition_k_subsets(nums: &[u32], k: usize) -> bool {
    // `used`: which numbers are in a bucket. The open bucket holds (sum of used) % target, so `used` is the
    // whole state, and a state that failed once fails every time: `dead` remembers it.
    fn fill(nums: &[u32], target: u32, used: u32, open: u32, dead: &mut [bool]) -> bool {
        if used == (1 << nums.len()) - 1 {
            return true;
        }
        if dead[used as usize] {
            return false;
        }
        let mut tried = 0; // equal numbers lead to the same states: try the first one only
        for i in 0..nums.len() {
            if used >> i & 1 == 1 || nums[i] == tried || open + nums[i] > target {
                continue;
            }
            if fill(nums, target, used | 1 << i, (open + nums[i]) % target, dead) {
                return true;
            }
            tried = nums[i];
            if open == 0 {
                break; // the largest unused number belongs to some bucket: this one is as good as any
            }
        }
        dead[used as usize] = true;
        false
    }
    let total: u32 = nums.iter().sum();
    if !total.is_multiple_of(k as u32) {
        return false;
    }
    let target = total / k as u32;
    let mut nums = nums.to_vec();
    nums.sort_unstable_by(|a, b| b.cmp(a));
    nums[0] <= target && fill(&nums, target, 0, 0, &mut vec![false; 1 << nums.len()])
}
