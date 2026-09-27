pub fn find_target_sum_ways(nums: &[u32], target: i32) -> u64 {
    let total: i64 = nums.iter().map(|&x| x as i64).sum();
    // The + numbers sum to P and the - numbers to total - P, so P = (total + target) / 2.
    let doubled = total + target as i64;
    if doubled < 0 || doubled > 2 * total || doubled % 2 == 1 {
        return 0;
    }
    let plus = (doubled / 2) as usize;
    // ways[s] = subsets of the numbers so far that sum to s.
    let mut ways = vec![0u64; plus + 1];
    ways[0] = 1;
    for &x in nums {
        let x = x as usize;
        for s in (x..=plus).rev() {
            ways[s] += ways[s - x]; // a 0 doubles every count: +0 and -0
        }
    }
    ways[plus]
}
