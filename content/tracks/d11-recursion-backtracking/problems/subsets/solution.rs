pub fn subsets(nums: &[i32]) -> Vec<Vec<i32>> {
    fn go(nums: &[i32], path: &mut Vec<i32>, out: &mut Vec<Vec<i32>>) {
        let Some((&first, rest)) = nums.split_first() else {
            out.push(path.clone());
            return;
        };
        go(rest, path, out); // leave `first` out
        path.push(first);
        go(rest, path, out); // take it
        path.pop();
    }
    let mut out = Vec::with_capacity(1 << nums.len());
    go(nums, &mut Vec::new(), &mut out);
    out
}
