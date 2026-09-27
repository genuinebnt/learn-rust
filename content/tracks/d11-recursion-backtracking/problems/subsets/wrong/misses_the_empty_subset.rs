pub fn subsets(nums: &[i32]) -> Vec<Vec<i32>> {
    fn go(nums: &[i32], start: usize, path: &mut Vec<i32>, out: &mut Vec<Vec<i32>>) {
        for i in start..nums.len() {
            path.push(nums[i]);
            out.push(path.clone());
            go(nums, i + 1, path, out);
            path.pop();
        }
    }
    let mut out = Vec::new();
    go(nums, 0, &mut Vec::new(), &mut out);
    out
}
