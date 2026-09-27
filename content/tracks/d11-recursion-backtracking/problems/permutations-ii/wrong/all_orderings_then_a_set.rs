pub fn permute_unique(nums: &[i32]) -> Vec<Vec<i32>> {
    fn go(v: &mut Vec<i32>, k: usize, seen: &mut std::collections::HashSet<Vec<i32>>) {
        if k == v.len() {
            seen.insert(v.clone());
            return;
        }
        for i in k..v.len() {
            v.swap(k, i);
            go(v, k + 1, seen);
            v.swap(k, i);
        }
    }
    let mut seen = std::collections::HashSet::new();
    go(&mut nums.to_vec(), 0, &mut seen);
    seen.into_iter().collect()
}
