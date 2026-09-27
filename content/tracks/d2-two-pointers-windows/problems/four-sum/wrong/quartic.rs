pub fn four_sum(nums: &[i32], target: i64) -> Vec<[i32; 4]> {
    let n = nums.len();
    let mut out = std::collections::BTreeSet::new();
    for a in 0..n {
        for b in a + 1..n {
            for c in b + 1..n {
                for d in c + 1..n {
                    if nums[a] as i64 + nums[b] as i64 + nums[c] as i64 + nums[d] as i64 == target {
                        let mut q = [nums[a], nums[b], nums[c], nums[d]];
                        q.sort();
                        out.insert(q);
                    }
                }
            }
        }
    }
    out.into_iter().collect()
}
