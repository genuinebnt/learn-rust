pub fn find_target_sum_ways(nums: &[u32], target: i32) -> u64 {
    let total: i64 = nums.iter().map(|&x| x as i64).sum();
    let doubled = total + target as i64;
    if doubled < 0 || doubled > 2 * total {
        return 0;
    }
    let plus = (doubled / 2) as usize;
    let mut ways = vec![0u64; plus + 1];
    ways[0] = 1;
    for &x in nums {
        let x = x as usize;
        for s in (x..=plus).rev() {
            ways[s] += ways[s - x];
        }
    }
    ways[plus]
}
