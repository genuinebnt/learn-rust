use std::collections::HashMap;

pub fn two_sum(nums: &[i32], target: i32) -> Option<(usize, usize)> {
    let mut seen: HashMap<i32, usize> = HashMap::with_capacity(nums.len());
    for (j, &x) in nums.iter().enumerate() {
        if let Some(&i) = seen.get(&(target - x)) {
            return Some((i, j));
        }
        seen.insert(x, j);
    }
    None
}
