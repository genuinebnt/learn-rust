use std::collections::HashSet;

pub fn longest_consecutive(nums: &[i32]) -> usize {
    let set: HashSet<i32> = nums.iter().copied().collect();
    let mut best = 0;
    for &x in &set {
        if set.contains(&(x - 1)) {
            continue;
        }
        let mut len = 1;
        let mut y = x;
        while set.contains(&(y + 1)) {
            y += 1;
            len += 1;
        }
        best = best.max(len);
    }
    best
}
