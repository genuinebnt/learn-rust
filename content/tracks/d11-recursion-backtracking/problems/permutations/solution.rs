pub fn permute(nums: &[i32]) -> Vec<Vec<i32>> {
    fn go(nums: &[i32], used: &mut [bool], path: &mut Vec<i32>, out: &mut Vec<Vec<i32>>) {
        if path.len() == nums.len() {
            out.push(path.clone());
            return;
        }
        for i in 0..nums.len() {
            if used[i] {
                continue;
            }
            used[i] = true;
            path.push(nums[i]);
            go(nums, used, path, out);
            path.pop();
            used[i] = false;
        }
    }
    let mut out = Vec::new();
    go(nums, &mut vec![false; nums.len()], &mut Vec::with_capacity(nums.len()), &mut out);
    out
}
