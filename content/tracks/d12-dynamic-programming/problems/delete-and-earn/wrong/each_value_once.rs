pub fn delete_and_earn(nums: &[u32]) -> u64 {
    let Some(&max) = nums.iter().max() else {
        return 0;
    };
    let mut points = vec![0u64; max as usize + 1];
    for &x in nums {
        points[x as usize] = x as u64;
    }
    let (mut before, mut best) = (0u64, 0u64);
    for &p in &points {
        (before, best) = (best, best.max(before + p));
    }
    best
}
