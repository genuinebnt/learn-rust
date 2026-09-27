pub fn permute(nums: &[i32]) -> Vec<Vec<i32>> {
    fn go(v: &mut Vec<i32>, k: usize, out: &mut Vec<Vec<i32>>) {
        if k == v.len() {
            out.push(v.clone());
            return;
        }
        for i in k..v.len() {
            v.swap(k, i);
            go(v, k + 1, out);
        }
    }
    let mut out = Vec::new();
    go(&mut nums.to_vec(), 0, &mut out);
    out
}
