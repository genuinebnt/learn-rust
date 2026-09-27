use std::collections::HashMap;

pub fn top_k_frequent(nums: &[i32], k: usize) -> Vec<i32> {
    let mut counts: HashMap<i32, usize> = HashMap::new();
    for &x in nums {
        *counts.entry(x).or_insert(0) += 1;
    }
    let mut by_count: Vec<(i32, usize)> = counts.into_iter().collect();
    by_count.sort_unstable_by(|a, b| b.1.cmp(&a.1).then(b.0.cmp(&a.0)));
    by_count.into_iter().take(k).map(|(x, _)| x).collect()
}
