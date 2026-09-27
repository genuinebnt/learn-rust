pub fn subsets_with_dup(nums: &[i32]) -> Vec<Vec<i32>> {
    fn go(nums: &[i32], start: usize, path: &mut Vec<i32>, out: &mut Vec<Vec<i32>>) {
        out.push(path.clone());
        for i in start..nums.len() {
            // Among equal values, only the first may be chosen at this depth.
            if i > start && nums[i] == nums[i - 1] {
                continue;
            }
            path.push(nums[i]);
            go(nums, i + 1, path, out);
            path.pop();
        }
    }
    let mut sorted = nums.to_vec();
    sorted.sort_unstable();
    let mut out = Vec::new();
    go(&sorted, 0, &mut Vec::new(), &mut out);
    out
}
