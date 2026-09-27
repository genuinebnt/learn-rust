use std::collections::HashSet;

pub fn contains_duplicate(nums: &[i32]) -> bool {
    let mut seen = HashSet::with_capacity(nums.len());
    nums.iter().any(|x| !seen.insert(x))
}
