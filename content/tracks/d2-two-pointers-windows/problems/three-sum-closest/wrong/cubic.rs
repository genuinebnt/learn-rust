pub fn three_sum_closest(nums: &[i32], target: i32) -> i32 {
    let n = nums.len();
    let mut best = nums[0] + nums[1] + nums[2];
    for i in 0..n {
        for j in i + 1..n {
            for k in j + 1..n {
                let sum = nums[i] + nums[j] + nums[k];
                if sum.abs_diff(target) < best.abs_diff(target) {
                    best = sum;
                }
            }
        }
    }
    best
}
