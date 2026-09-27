pub fn max_coins(nums: &[u32]) -> u64 {
    let mut v: Vec<u64> = nums.iter().map(|&x| x as u64).collect();
    let mut total = 0;
    while !v.is_empty() {
        let k = (0..v.len()).min_by_key(|&i| v[i]).unwrap();
        let left = if k > 0 { v[k - 1] } else { 1 };
        let right = if k + 1 < v.len() { v[k + 1] } else { 1 };
        total += left * v[k] * right;
        v.remove(k);
    }
    total
}
