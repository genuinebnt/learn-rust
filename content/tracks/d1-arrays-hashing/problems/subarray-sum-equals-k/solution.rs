use std::collections::HashMap;

pub fn subarray_sum(nums: &[i32], k: i32) -> usize {
    let mut seen: HashMap<i64, usize> = HashMap::from([(0, 1)]);
    let (mut sum, mut count) = (0i64, 0usize);
    for &x in nums {
        sum += x as i64;
        count += seen.get(&(sum - k as i64)).copied().unwrap_or(0);
        *seen.entry(sum).or_insert(0) += 1;
    }
    count
}
