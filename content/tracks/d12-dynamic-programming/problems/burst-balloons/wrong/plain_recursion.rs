fn best(v: &mut Vec<u64>) -> u64 {
    let mut top = 0;
    for k in 0..v.len() {
        let left = if k > 0 { v[k - 1] } else { 1 };
        let right = if k + 1 < v.len() { v[k + 1] } else { 1 };
        let x = v.remove(k);
        top = top.max(left * x * right + best(v));
        v.insert(k, x);
    }
    top
}

pub fn max_coins(nums: &[u32]) -> u64 {
    let mut v: Vec<u64> = nums.iter().map(|&x| x as u64).collect();
    best(&mut v)
}
