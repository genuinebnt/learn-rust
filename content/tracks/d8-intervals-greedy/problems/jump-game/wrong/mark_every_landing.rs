pub fn can_jump(nums: &[u32]) -> bool {
    let n = nums.len();
    let mut ok = vec![false; n];
    ok[0] = true;
    for i in 0..n {
        if ok[i] {
            for j in i + 1..=(i + nums[i] as usize).min(n - 1) {
                ok[j] = true;
            }
        }
    }
    ok[n - 1]
}
