use std::collections::HashMap;

pub fn two_sum(nums: &[i32], target: i32) -> Option<(usize, usize)> {
    let mut seen: HashMap<i32, usize> = HashMap::new();
    for (j, &x) in nums.iter().enumerate() {
        seen.insert(x, j);
        if let Some(&i) = seen.get(&(target - x)) {
            return Some((i.min(j), i.max(j)));
        }
    }
    None
}
