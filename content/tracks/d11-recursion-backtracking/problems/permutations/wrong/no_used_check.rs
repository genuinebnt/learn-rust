pub fn permute(nums: &[i32]) -> Vec<Vec<i32>> {
    fn go(nums: &[i32], path: &mut Vec<i32>, out: &mut Vec<Vec<i32>>) {
        if path.len() == nums.len() {
            out.push(path.clone());
            return;
        }
        for &x in nums {
            path.push(x);
            go(nums, path, out);
            path.pop();
        }
    }
    let mut out = Vec::new();
    go(nums, &mut Vec::new(), &mut out);
    out
}
