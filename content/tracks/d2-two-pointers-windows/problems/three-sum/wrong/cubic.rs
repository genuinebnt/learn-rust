pub fn three_sum(nums: &[i32]) -> Vec<[i32; 3]> {
    let mut out = std::collections::BTreeSet::new();
    let n = nums.len();
    for i in 0..n {
        for j in i + 1..n {
            for k in j + 1..n {
                if nums[i] as i64 + nums[j] as i64 + nums[k] as i64 == 0 {
                    let mut t = [nums[i], nums[j], nums[k]];
                    t.sort();
                    out.insert(t);
                }
            }
        }
    }
    out.into_iter().collect()
}
