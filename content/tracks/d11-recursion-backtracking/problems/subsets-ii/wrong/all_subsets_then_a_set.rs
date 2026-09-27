pub fn subsets_with_dup(nums: &[i32]) -> Vec<Vec<i32>> {
    let mut sorted = nums.to_vec();
    sorted.sort();
    let mut seen = std::collections::HashSet::new();
    for mask in 0..1u64 << sorted.len() {
        let s: Vec<i32> = (0..sorted.len()).filter(|&i| mask >> i & 1 == 1).map(|i| sorted[i]).collect();
        seen.insert(s);
    }
    seen.into_iter().collect()
}
